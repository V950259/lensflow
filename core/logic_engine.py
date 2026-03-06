from datetime import datetime
import urllib.parse

class LogicEngine:
    def __init__(self):
        # 预设的常见过敏原清单
        self.allergen_list = [
            "花生", "牛奶", "鸡蛋", "大豆", "小麦", "坚果", "鱼", "海鲜", "虾", "蟹", "芒果", "菠萝"
        ]

    def parse_calendar_data(self, event_name, time_str, location):
        """
        生成 Google Calendar 的 Web 添加链接
        time_str 格式预期: YYYY-MM-DD HH:MM
        """
        try:
            # 尝试解析时间
            dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
            # 格式化为 Google Calendar 需要的格式: YYYYMMDDTHHMMSS
            start_time = dt.strftime("%Y%m%dT%H%M00")
            # 默认活动持续 1 小时
            end_time = dt.replace(hour=dt.hour + 1).strftime("%Y%m%dT%H%M00") if dt.hour < 23 else start_time
            
            dates = f"{start_time}/{end_time}"
            
            # 构建 Google Calendar Link
            base_url = "https://calendar.google.com/calendar/render"
            params = {
                "action": "TEMPLATE",
                "text": event_name,
                "dates": dates,
                "location": location,
                "details": "由 LensFlow 自动提取"
            }
            return f"{base_url}?{urllib.parse.urlencode(params)}"
        except Exception as e:
            print(f"Date Parse Error: {e}")
            return None

    def analyze_health_risk(self, ingredients):
        """
        对比成分与过敏原清单，返回风险列表
        ingredients: list of strings
        """
        risks = []
        if not ingredients:
            return risks
            
        for ingredient in ingredients:
            for allergen in self.allergen_list:
                if allergen in ingredient:
                    risks.append(allergen)
        
        return list(set(risks)) # 去重
