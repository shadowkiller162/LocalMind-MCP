#!/usr/bin/env python3
"""
LM Studio Auto-Evict 和 JIT Loading 測試腳本

此腳本用於驗證 LM Studio 的 Auto-Evict 和 JIT Loading 配置是否正確啟用。
"""

import sys
import time
import requests
from typing import Dict, Any

# 確保能夠 import Django 設定
import os
import django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from mcp.config import get_config


def test_auto_evict_configuration() -> None:
    """測試 Auto-Evict 和 JIT Loading 配置"""
    
    config = get_config()
    chat_url = f"http://{config.lmstudio_host}:{config.lmstudio_port}/v1/chat/completions"
    
    print("=" * 60)
    print("🧪 LM Studio Auto-Evict 和 JIT Loading 測試")
    print("=" * 60)
    
    # 測試模型列表
    test_models = [
        "deepseek-r1-distill-qwen-7b",
        "deepseek-r1-0528-qwen3-8b"
    ]
    
    # 測試1: 檢查當前記憶體狀態
    print("\n📊 測試1: 檢查當前記憶體狀態")
    memory_status = check_memory_status(chat_url)
    print(f"結果: {memory_status}")
    
    # 測試2: JIT Loading 測試
    print("\n⚡ 測試2: JIT Loading 效能測試")
    for i, model in enumerate(test_models, 1):
        print(f"\n{i}. 載入模型: {model}")
        load_time, success, used_model = test_model_loading(chat_url, model)
        
        if success:
            print(f"   ✅ 成功載入: {used_model}")
            print(f"   ⏱️  載入時間: {load_time:.1f}秒")
            
            # 分析載入類型
            if load_time > 10.0:
                print("   🎯 JIT Loading 已啟用 (載入時間 >10秒)")
            elif load_time > 5.0:
                print("   ⚡ JIT Loading 可能啟用 (載入時間 5-10秒)")
            elif load_time > 2.0:
                print("   ⚠️  部分載入或快取 (載入時間 2-5秒)")
            else:
                print("   ❌ 模型已在記憶體中 (載入時間 <2秒)")
        else:
            print(f"   ❌ 載入失敗")
    
    # 測試3: Auto-Evict 驗證
    print("\n🔄 測試3: Auto-Evict 功能驗證")
    auto_evict_result = test_auto_evict_behavior(chat_url, test_models)
    
    # 測試4: TTL 測試 (短 TTL)
    print("\n⏰ 測試4: TTL (Time-To-Live) 功能測試")
    ttl_result = test_ttl_behavior(chat_url, test_models[0])
    
    # 綜合結果分析
    print("\n" + "=" * 60)
    print("📋 測試結果總結")
    print("=" * 60)
    
    analyze_results(memory_status, auto_evict_result, ttl_result)
    
    # 提供配置建議
    print("\n💡 配置建議")
    print("-" * 30)
    provide_configuration_recommendations(auto_evict_result)


def check_memory_status(chat_url: str) -> Dict[str, Any]:
    """檢查當前記憶體中的模型狀態"""
    try:
        # 發送無指定模型的請求
        response = requests.post(chat_url, json={
            'messages': [{'role': 'user', 'content': 'test'}],
            'max_tokens': 1
        }, timeout=10)
        
        if response.status_code == 404:
            error_data = response.json()
            error_message = error_data.get('error', {}).get('message', '')
            
            if 'Multiple models are loaded' in error_message:
                # 解析載入的模型列表
                models_in_memory = []
                lines = error_message.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('Multiple') and not line.startswith('Your models'):
                        models_in_memory.append(line)
                
                return {
                    'status': 'multiple_models_loaded',
                    'models_count': len(models_in_memory),
                    'models': models_in_memory,
                    'auto_evict_enabled': False
                }
            else:
                return {
                    'status': 'no_models_loaded',
                    'models_count': 0,
                    'auto_evict_enabled': True
                }
        
        elif response.status_code == 200:
            result = response.json()
            return {
                'status': 'single_model_loaded',
                'models_count': 1,
                'default_model': result.get('model'),
                'auto_evict_enabled': True
            }
        
        else:
            return {'status': 'error', 'error': f'HTTP {response.status_code}'}
            
    except Exception as e:
        return {'status': 'error', 'error': str(e)}


def test_model_loading(chat_url: str, model_name: str, ttl: int = 1800) -> tuple:
    """測試單一模型載入時間"""
    try:
        start_time = time.time()
        
        response = requests.post(chat_url, json={
            'model': model_name,
            'messages': [{'role': 'user', 'content': 'test'}],
            'max_tokens': 1,
            'temperature': 0,
            'ttl': ttl
        }, timeout=120)  # 給 JIT Loading 足夠時間 (2分鐘)
        
        load_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            used_model = result.get('model', model_name)
            return load_time, True, used_model
        else:
            return load_time, False, None
            
    except Exception as e:
        return 0, False, str(e)


def test_auto_evict_behavior(chat_url: str, models: list) -> Dict[str, Any]:
    """測試 Auto-Evict 行為"""
    if len(models) < 2:
        return {'error': 'Need at least 2 models for testing'}
    
    print(f"   📝 依序載入兩個模型測試 Auto-Evict...")
    
    # 載入第一個模型
    load_time1, success1, model1 = test_model_loading(chat_url, models[0])
    print(f"   1️⃣ {models[0]}: {load_time1:.1f}秒")
    
    if not success1:
        return {'error': f'Failed to load first model: {models[0]}'}
    
    # 立即載入第二個模型
    load_time2, success2, model2 = test_model_loading(chat_url, models[1])
    print(f"   2️⃣ {models[1]}: {load_time2:.1f}秒")
    
    if not success2:
        return {'error': f'Failed to load second model: {models[1]}'}
    
    # 檢查記憶體狀態
    memory_status = check_memory_status(chat_url)
    
    # 分析結果
    auto_evict_working = False
    if memory_status.get('status') == 'single_model_loaded':
        auto_evict_working = True
    elif memory_status.get('models_count', 0) <= 1:
        auto_evict_working = True
    
    return {
        'first_load_time': load_time1,
        'second_load_time': load_time2,
        'auto_evict_working': auto_evict_working,
        'final_memory_status': memory_status,
        'jit_loading_detected': load_time2 > 8.0
    }


def test_ttl_behavior(chat_url: str, model_name: str) -> Dict[str, Any]:
    """測試 TTL 行為（使用短 TTL 進行快速測試）"""
    short_ttl = 10  # 10秒 TTL 用於快速測試
    
    print(f"   ⏱️ 載入模型並設定 {short_ttl}秒 TTL...")
    
    # 載入模型並設定短 TTL
    load_time, success, used_model = test_model_loading(chat_url, model_name, short_ttl)
    
    if not success:
        return {'error': 'Failed to load model with TTL'}
    
    print(f"   ✅ 模型載入完成，等待 {short_ttl + 5}秒後測試是否被卸載...")
    time.sleep(short_ttl + 5)  # 等待 TTL 過期
    
    # 檢查模型是否被卸載
    memory_status = check_memory_status(chat_url)
    
    # 再次載入同一模型（應該觸發 JIT）
    reload_time, reload_success, _ = test_model_loading(chat_url, model_name)
    
    return {
        'initial_load_time': load_time,
        'ttl_seconds': short_ttl,
        'memory_after_ttl': memory_status,
        'reload_time': reload_time,
        'ttl_working': reload_time > 8.0,  # 重新載入時間長表示 TTL 生效
        'reload_success': reload_success
    }


def analyze_results(memory_status: Dict, auto_evict_result: Dict, ttl_result: Dict) -> None:
    """分析測試結果"""
    
    print(f"🔍 記憶體狀態: {memory_status.get('status', 'unknown')}")
    if memory_status.get('models_count'):
        print(f"   模型數量: {memory_status['models_count']}")
    
    if 'auto_evict_working' in auto_evict_result:
        auto_evict_status = "✅ 已啟用" if auto_evict_result['auto_evict_working'] else "❌ 未啟用"
        print(f"🔄 Auto-Evict: {auto_evict_status}")
        
        if auto_evict_result.get('jit_loading_detected'):
            print("⚡ JIT Loading: ✅ 已啟用")
        else:
            print("⚡ JIT Loading: ❌ 未檢測到")
    
    if 'ttl_working' in ttl_result:
        ttl_status = "✅ 正常運作" if ttl_result['ttl_working'] else "❌ 未生效"
        print(f"⏰ TTL 功能: {ttl_status}")


def provide_configuration_recommendations(auto_evict_result: Dict) -> None:
    """提供配置建議"""
    
    if not auto_evict_result.get('auto_evict_working', False):
        print("❌ Auto-Evict 未啟用，請執行以下步驟:")
        print("   1. 打開 LM Studio 應用程式")
        print("   2. 前往 Developer 標籤頁")
        print("   3. 在 Server Settings 中啟用 Auto-Evict")
        print("   4. 重啟 LM Studio Server")
        print("   5. 重新執行此測試")
    else:
        print("✅ Auto-Evict 配置正確")
    
    if not auto_evict_result.get('jit_loading_detected', False):
        print("❌ JIT Loading 未檢測到，建議:")
        print("   1. 確認 LM Studio 版本 >= 0.3.9")
        print("   2. 檢查模型是否手動預載入")
        print("   3. 重啟 LM Studio 清除記憶體")
    else:
        print("✅ JIT Loading 運作正常")


if __name__ == "__main__":
    test_auto_evict_configuration()