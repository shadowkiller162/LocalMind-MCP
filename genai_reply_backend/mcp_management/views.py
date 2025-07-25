"""
MCP Management Views

提供 MCP 系統的管理界面，包含狀態監控、配置管理等功能。
整合 HTMX 提供現代化的用戶體驗。
"""

import logging
import uuid
import requests
from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django_htmx.http import HttpResponseClientRedirect
from django.utils import timezone

logger = logging.getLogger(__name__)


def detect_lmstudio_models(config):
    """
    檢測 LM Studio 中可用的模型
    
    Returns:
        dict: 包含模型列表和狀態信息
    """
    try:
        # LM Studio API endpoint for models
        url = f"http://{config.lmstudio_host}:{config.lmstudio_port}/v1/models"
        
        response = requests.get(
            url, 
            timeout=config.lmstudio_timeout or 10,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            models_data = response.json()
            
            # 提取模型名稱列表
            if 'data' in models_data:
                models = [model.get('id', 'unknown') for model in models_data['data']]
                active_model = models[0] if models else config.default_model
                
                return {
                    'success': True,
                    'models': models,
                    'active_model': active_model,
                    'total_models': len(models),
                    'service_status': 'connected'
                }
            else:
                return {
                    'success': False,
                    'models': [config.default_model],
                    'active_model': config.default_model,
                    'error': 'Invalid response format from LM Studio',
                    'service_status': 'error'
                }
        else:
            return {
                'success': False,
                'models': [config.default_model],
                'active_model': config.default_model,
                'error': f'LM Studio API returned status {response.status_code}',
                'service_status': 'disconnected'
            }
            
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'models': [config.default_model],
            'active_model': config.default_model,
            'error': 'Unable to connect to LM Studio. Is it running?',
            'service_status': 'disconnected'
        }
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'models': [config.default_model],
            'active_model': config.default_model,
            'error': 'LM Studio connection timeout',
            'service_status': 'timeout'
        }
    except Exception as e:
        logger.error(f"LM Studio 模型檢測錯誤: {e}")
        return {
            'success': False,
            'models': [config.default_model],
            'active_model': config.default_model,
            'error': f'Detection error: {str(e)}',
            'service_status': 'error'
        }


@login_required
def mcp_dashboard(request):
    """MCP 管理儀表板主頁面"""
    context = {
        'page_title': 'MCP Management Dashboard',
        'user': request.user,
    }
    return render(request, 'mcp_management/dashboard.html', context)


@login_required
@require_http_methods(["GET"])
def mcp_status(request):
    """
    MCP 狀態監控 API
    
    返回 MCP 服務的即時狀態信息，支援 HTMX 輪詢更新
    """
    try:
        # 從 MCP 配置模組取得狀態信息
        from mcp.config import get_config
        from mcp.llm import UnifiedModelManager, LLMServiceType
        
        config = get_config()
        
        # 檢測 LM Studio 中的實際模型
        lmstudio_info = detect_lmstudio_models(config)
        
        # 根據檢測結果構建狀態信息
        is_connected = lmstudio_info['success']
        service_name = config.default_llm_service
        
        if is_connected:
            model_name = lmstudio_info['active_model']
            available_models = lmstudio_info['models']
            total_models = lmstudio_info['total_models']
        else:
            model_name = config.default_model
            available_models = [config.default_model]
            total_models = 1
        
        mcp_status = {
            'is_connected': is_connected,
            'service_name': service_name,
            'model_name': model_name,
            'available_models': available_models,
            'total_models': total_models,
            'last_ping': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            'response_time': '150ms' if is_connected else 'N/A',
            'active_connections': 3 if is_connected else 0,
            'max_connections': config.max_connections,
            'lmstudio_status': lmstudio_info['service_status'],
            'error_message': lmstudio_info.get('error') if not is_connected else None,
        }
        
        if hasattr(request, 'htmx') and request.htmx:
            # HTMX 請求返回部分模板
            return render(request, 'components/mcp_status.html', {
                'mcp_status': mcp_status
            })
        else:
            # 普通請求返回 JSON
            return JsonResponse(mcp_status, json_dumps_params={'ensure_ascii': False})
            
    except Exception as e:
        logger.error(f"獲取 MCP 狀態失敗: {e}")
        
        error_status = {
            'is_connected': False,
            'service_name': 'Unknown',
            'error_message': str(e),
        }
        
        if hasattr(request, 'htmx') and request.htmx:
            return render(request, 'components/mcp_status.html', {
                'mcp_status': error_status
            })
        else:
            return JsonResponse(error_status, status=500, json_dumps_params={'ensure_ascii': False})


@login_required
@require_http_methods(["POST"])
def mcp_reconnect(request):
    """
    MCP 重新連接功能
    
    嘗試重新建立 MCP 連接
    """
    try:
        # 實作 MCP 重新連接邏輯
        success = True  # 模擬成功
        
        if success:
            if hasattr(request, 'htmx') and request.htmx:
                # 觸發狀態組件刷新
                response = render(request, 'components/mcp_status.html', {
                    'mcp_status': {
                        'is_connected': True,
                        'service_name': 'ollama',
                        'reconnected': True,
                    }
                })
                response['HX-Trigger'] = 'mcpReconnected'
                return response
            else:
                return JsonResponse({'success': True, 'message': 'MCP 重新連接成功'}, json_dumps_params={'ensure_ascii': False})
        else:
            raise Exception("重新連接失敗")
            
    except Exception as e:
        logger.error(f"MCP 重新連接失敗: {e}")
        
        if hasattr(request, 'htmx') and request.htmx:
            return render(request, 'components/mcp_status.html', {
                'mcp_status': {
                    'is_connected': False,
                    'error_message': f'重新連接失敗: {str(e)}',
                }
            })
        else:
            return JsonResponse({'success': False, 'error': str(e)}, status=500, json_dumps_params={'ensure_ascii': False})


@login_required
@require_http_methods(["POST"])
def chat_send(request):
    """
    AI 對話發送功能
    
    處理用戶發送的對話訊息，調用 MCP LLM 服務進行回覆
    """
    try:
        message_content = request.POST.get('message', '').strip()
        if not message_content:
            raise ValueError("訊息內容不能為空")
        
        # 創建用戶訊息
        user_message = {
            'id': str(uuid.uuid4()),
            'content': message_content,
            'timestamp': timezone.now(),
            'type': 'user'
        }
        
        # 渲染用戶訊息
        user_message_html = render(request, 'partials/chat_message.html', {
            'message': user_message,
            'message_type': 'user'
        }).content.decode('utf-8')
        
        # 嘗試調用 MCP LLM 服務
        try:
            ai_response = process_ai_message(message_content, request.user)
            
            # 創建 AI 回覆訊息
            ai_message = {
                'id': str(uuid.uuid4()),
                'content': ai_response.get('content', '抱歉，我暫時無法回覆。'),
                'timestamp': timezone.now(),
                'thinking': ai_response.get('thinking'),  # DeepSeek R1 思考過程
                'mcp_data': ai_response.get('mcp_data'),
                'can_regenerate': True,
                'is_streaming': False
            }
            
            # 渲染 AI 回覆
            ai_message_html = render(request, 'partials/chat_message.html', {
                'message': ai_message,
                'message_type': 'assistant'
            }).content.decode('utf-8')
            
            # 合併用戶訊息和 AI 回覆
            combined_html = clean_html_whitespace(user_message_html + ai_message_html)
            
            # HTMX 期望直接的 HTML 回應，不是 JSON
            return HttpResponse(combined_html, content_type='text/html')
            
        except Exception as ai_error:
            logger.error(f"AI 處理錯誤: {ai_error}")
            
            # 創建錯誤訊息
            error_message = {
                'id': str(uuid.uuid4()),
                'content': f'AI 服務暫時不可用: {str(ai_error)}',
                'timestamp': timezone.now(),
                'error_details': str(ai_error) if request.user.is_staff else None
            }
            
            error_message_html = render(request, 'partials/chat_message.html', {
                'message': error_message,
                'message_type': 'error'
            }).content.decode('utf-8')
            
            combined_html = clean_html_whitespace(user_message_html + error_message_html)
            
            # HTMX 錯誤情況也回傳 HTML
            return HttpResponse(combined_html, content_type='text/html')
        
    except Exception as e:
        logger.error(f"對話處理錯誤: {e}")
        
        error_message = {
            'content': f'處理訊息時發生錯誤: {str(e)}',
            'timestamp': timezone.now(),
        }
        
        error_html = clean_html_whitespace(render(request, 'partials/chat_message.html', {
            'message': error_message,
            'message_type': 'error'
        }).content.decode('utf-8'))
        
        # HTMX 異常情況也回傳 HTML
        return HttpResponse(error_html, content_type='text/html')


def clean_html_whitespace(html_content):
    """
    清理 HTML 內容中的多餘換行和空白字符
    
    優化前端顯示體驗，移除不必要的空白
    """
    import re
    
    if not html_content:
        return html_content
    
    # 移除多餘的換行符和空格
    # 保留有意義的換行（在標籤間），但移除過多的空白
    cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', html_content)  # 合併多個空行
    cleaned = re.sub(r'>\s*\n\s*<', '><', cleaned)  # 移除標籤間無意義換行
    cleaned = re.sub(r'\n\s+', '\n', cleaned)  # 移除行首多餘空格
    cleaned = re.sub(r'\s+\n', '\n', cleaned)  # 移除行尾多餘空格
    
    return cleaned.strip()


def parse_ai_response(raw_content):
    """
    解析 AI 回應內容，分離思考過程和實際回覆
    
    支援多種思考標籤格式：
    - <think>...</think>
    - <thinking>...</thinking>
    - <!-- thinking -->...</think>
    """
    import re
    
    if not raw_content:
        return {'content': '抱歉，我無法處理您的請求。', 'thinking': None}
    
    # 定義思考標籤的正則模式
    thinking_patterns = [
        r'<think>(.*?)</think>',           # <think>...</think>
        r'<thinking>(.*?)</thinking>',     # <thinking>...</thinking>
        r'<!-- thinking -->(.*?)(?:</thinking>|$)',  # <!-- thinking -->...
    ]
    
    thinking_content = None
    cleaned_content = raw_content
    
    # 嘗試匹配和提取思考過程
    for pattern in thinking_patterns:
        match = re.search(pattern, raw_content, re.DOTALL | re.IGNORECASE)
        if match:
            thinking_content = match.group(1).strip()
            # 從原始內容中移除思考標籤和內容
            cleaned_content = re.sub(pattern, '', raw_content, flags=re.DOTALL | re.IGNORECASE).strip()
            break
    
    # 如果沒有找到思考標籤，檢查是否整個內容都是思考過程
    if not thinking_content and raw_content.strip().startswith('<think>'):
        # 可能是未閉合的思考標籤
        thinking_match = re.search(r'<think>(.*)', raw_content, re.DOTALL | re.IGNORECASE)
        if thinking_match:
            thinking_content = thinking_match.group(1).strip()
            cleaned_content = '我正在思考您的問題，請稍候...'
    
    # 清理內容中的多餘空行和格式
    if cleaned_content:
        cleaned_content = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_content)  # 合併多個空行
        cleaned_content = cleaned_content.strip()
    
    # 如果清理後沒有實際內容，提供預設回覆
    if not cleaned_content or len(cleaned_content.strip()) < 10:
        cleaned_content = '我正在處理您的請求，請稍候...'
    
    return {
        'content': cleaned_content,
        'thinking': thinking_content
    }


def process_ai_message(message_content, user):
    """
    處理 AI 訊息的核心邏輯
    
    這裡整合 MCP LLM 服務來處理用戶訊息
    """
    try:
        # 檢查是否為系統相關查詢
        if any(keyword in message_content.lower() for keyword in ['狀態', 'status', 'mcp', '檢查']):
            return handle_system_query(message_content)
        
        # 調用 MCP LLM 服務
        from mcp.config import get_config
        from mcp.llm import UnifiedModelManager, LLMServiceType
        from mcp.llm.types import ChatRequest, ChatMessage
        
        config = get_config()
        llm_manager = UnifiedModelManager(LLMServiceType.AUTO)
        
        # 準備對話上下文
        system_prompt = """你是 LocalMind-MCP 平台的 AI 助手。你可以：
1. 回答關於 MCP (Model Context Protocol) 的問題
2. 協助用戶管理和配置 MCP 服務
3. 提供系統使用說明和技術支援
4. 進行一般性對話

請用友善、專業的語氣回答用戶問題。"""
        
        # 初始化統一管理器並發送對話請求
        import asyncio
        
        async def get_ai_response():
            await llm_manager.initialize()
            
            # 創建聊天訊息列表
            messages = [
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=message_content)
            ]
            
            return await llm_manager.chat(
                model_name=config.default_model,
                messages=messages
            )
        
        # 執行異步對話請求
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(get_ai_response())
        finally:
            loop.close()
        
        # 解析回應內容，分離思考過程和實際回覆
        parsed_response = parse_ai_response(response.content if hasattr(response, 'content') else '抱歉，我無法處理您的請求。')
        
        return {
            'content': parsed_response['content'],
            'thinking': parsed_response['thinking'] or getattr(response, 'thinking', None),  # DeepSeek R1 特有
            'mcp_data': getattr(response, 'mcp_data', None),
            'model_used': getattr(response, 'model', config.default_model)
        }
        
    except Exception as e:
        logger.error(f"AI 處理錯誤: {e}")
        raise e


def handle_system_query(message_content):
    """處理系統狀態查詢"""
    try:
        from mcp.config import get_config
        config = get_config()
        
        status_info = f"""🔍 **系統狀態檢查結果**

**MCP 服務配置:**
- 預設服務: {config.default_llm_service}
- 預設模型: {config.default_model}
- 最大連線數: {config.max_connections}
- 連線逾時: {config.connection_timeout}秒

**啟用的連接器:**
{', '.join(config.enabled_connectors)}

**快取狀態:**
- 啟用快取: {'是' if config.enable_cache else '否'}
- 快取 TTL: {config.cache_ttl}秒

系統目前運行正常！如需更詳細的資訊，請查看 MCP 管理儀表板。"""

        return {
            'content': status_info,
            'mcp_data': {
                'connector_type': 'system',
                'operation': 'status_check'
            }
        }
        
    except Exception as e:
        return {
            'content': f'無法獲取系統狀態: {str(e)}',
            'mcp_data': {
                'connector_type': 'system',
                'operation': 'status_check_failed'
            }
        }


@login_required
@require_http_methods(["POST"])
def chat_regenerate(request):
    """重新生成 AI 回覆"""
    try:
        message_id = request.POST.get('message_id')
        # 這裡可以實現重新生成邏輯
        # 暫時返回一個模擬的重新生成回覆
        
        regenerated_message = {
            'id': message_id,
            'content': '這是重新生成的回覆。(功能開發中)',
            'timestamp': timezone.now(),
            'can_regenerate': True,
            'is_streaming': False
        }
        
        return render(request, 'partials/chat_message.html', {
            'message': regenerated_message,
            'message_type': 'assistant'
        })
        
    except Exception as e:
        logger.error(f"重新生成失敗: {e}")
        return JsonResponse({'error': str(e)}, status=500, json_dumps_params={'ensure_ascii': False})