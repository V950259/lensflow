from openai import AsyncOpenAI
import json
import asyncio

class LensAI:
    def __init__(self, api_key, base_url, model_name="gpt-4o"):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model_name = model_name

    async def get_vision_response(self, base64_image, user_context=None):
        """
        异步分析图片并返回 JSON 格式的场景数据
        user_context: Optional dictionary containing user medical history and preferences
        """
        context_str = ""
        if user_context:
            context_str = f"""
            User Context:
            - Medical History/Allergies: {user_context.get('medical_history', 'None')}
            - Preferences: {user_context.get('preferences', 'None')}
            
            IMPORTANT: When analyzing "food_medicine" items, you MUST strictly cross-reference the extracted ingredients with the user's Medical History and Allergies.
            If ANY ingredient matches a known allergen or conflicts with a medical condition, set the 'risk_warning' field to a specific, high-priority warning message detailing the conflict.
            """

        prompt = f"""
        请分析这张图片。{context_str}
        你需要先判断图片属于以下哪种场景：
        1. "poster_notice": 包含活动海报、会议通知、日程表等。需要提取时间和地点。
        2. "food_medicine": 包含药盒、药品说明书、食品包装、食物等。需要分析成分、用法用量（如果是药品）、热量/营养（如果是食品）并给出健康/过敏风险提示。
        3. "general": 其他普通物体或场景。进行百科式介绍。

        请以 JSON 格式返回结果，不要包含 Markdown 格式标记（如 ```json），直接返回 JSON 对象。
        JSON 结构如下：
        {{
            "category": "poster_notice" | "food_medicine" | "general",
            "title": "简短的标题",
            "description": "对图片的简要描述",
            "data": {{
                // 如果是 poster_notice
                "event_name": "活动名称",
                "time": "时间 (YYYY-MM-DD HH:MM)",
                "location": "地点",
                
                // 如果是 food_medicine
                "sub_category": "food" | "medicine",
                "name": "产品名称",
                "ingredients": ["成分1", "成分2"],
                "risk_warning": "健康风险或过敏提示 (结合用户上下文)",
                "dosage_usage": "用法用量 (仅药品, 如 '每日2次, 每次1片')",
                "calories": "预估热量 (仅食品, 如 '250kcal/100g')",
                "health_tags": ["低脂", "高糖", "需冷藏"],
                
                // 如果是 general
                "knowledge": "相关的百科知识介绍"
            }}
        }}
        """

        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ],
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            print(f"Vision API Error: {e}")
            return None

    async def get_chat_response(self, messages):
        """
        进行多轮对话 (异步)
        messages: 标准 OpenAI 消息列表 [{"role": "user", "content": ...}, ...]
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"对话出错: {e}"
