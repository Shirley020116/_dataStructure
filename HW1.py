import os
import asyncio
import pandas as pd
from dotenv import load_dotenv
import io

# 根據你的專案結構調整下列 import
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.agents.web_surfer import MultimodalWebSurfer

load_dotenv()

#HW1 Price Analysis and provide suggestion about crypto price
async def process_chunk(chunk, start_idx, total_records, model_client, termination_condition):
    """
    處理單一批次資料：
    - 將該批次資料轉成 dict 格式
    - 組出提示，要求各代理人根據該批次資料進行分析，
        並提供加密貨幣價格建議。
    """
    # 將資料轉成 dict 格式
    chunk_data = chunk.to_dict(orient='records')
    
    # HW1 According to the cypto price to provide some recommendation and notice
    prompt = (
        f"目前正在處理第 {start_idx} 至 {start_idx + len(chunk) - 1} 筆資料（共 {total_records} 筆）。\n"
        f"以下為該批次資料:\n{chunk_data}\n\n"
        "請根據上述資料進行分析並提供加密貨幣市場的建議，注意事項：\n"
        "  1. 分析資料中的價格變動、趨勢及可能影響因素。\n"
        "  2. 提供相應的投資建議或其他有價值的市場洞察。\n"
        "請提供具體的結論與參考資訊。\n"
    )
    
    # 為每個批次建立新的 agent 與 team 實例
    local_data_agent = AssistantAgent("data_agent", model_client)
    local_web_surfer = MultimodalWebSurfer("web_surfer", model_client)
    local_assistant = AssistantAgent("assistant", model_client)
    local_user_proxy = UserProxyAgent("user_proxy")
    local_team = RoundRobinGroupChat(
        [local_data_agent, local_web_surfer, local_assistant, local_user_proxy],
        termination_condition=termination_condition
    )
    
    # 收集所有回覆訊息
    messages = []
    async for event in local_team.run_stream(task=prompt):
        if isinstance(event, TextMessage):
            # 印出目前哪個 agent 正在運作，方便追蹤
            print(f"[{event.source}] => {event.content}\n")
            messages.append({
                "batch_start": start_idx,
                "batch_end": start_idx + len(chunk) - 1,
                "source": event.source,
                "content": event.content,
                "type": event.type,
                "prompt_tokens": event.models_usage.prompt_tokens if event.models_usage else None,
                "completion_tokens": event.models_usage.completion_tokens if event.models_usage else None
            })
    return messages

async def main():
    # 載入環境變數
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        print("請檢查 .env 檔案中的 GEMINI_API_KEY。")
        return

    # 初始化模型用戶端 (此處示範使用 gemini-2.0-flash)
    model_client = OpenAIChatCompletionClient(
        model="gemini-2.0-flash",
        api_key=gemini_api_key,
    )
    
    termination_condition = TextMentionTermination("exit")
    
    # 使用 pandas 以 chunksize 方式讀取 CSV 檔案
    csv_file_path = "crypto_prices_daily.csv"  # 修改為你的加密貨幣資料檔案路徑
    chunk_size = 1000  # 可以調整批次大小
    chunks = list(pd.read_csv(csv_file_path, chunksize=chunk_size))
    total_records = sum(chunk.shape[0] for chunk in chunks)
    
    # 利用 map 與 asyncio.gather 同時處理所有批次（避免使用傳統 for 迴圈）
    tasks = list(map(
        lambda idx_chunk: process_chunk(
            idx_chunk[1],
            idx_chunk[0] * chunk_size,
            total_records,
            model_client,
            termination_condition
        ),
        enumerate(chunks)
    ))
    
    # 收集所有批次的結果
    results = await asyncio.gather(*tasks)
    
    # 將所有批次的訊息平坦化成一個清單
    all_messages = [msg for batch in results for msg in batch]
    
    # 將對話紀錄整理成 DataFrame 並存成 CSV
    df_log = pd.DataFrame(all_messages)
    output_file = "all_conversation_log.csv"  # 儲存對話紀錄的檔案
    df_log.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"已將所有對話紀錄輸出為 {output_file}")

if __name__ == '__main__':
    asyncio.run(main())