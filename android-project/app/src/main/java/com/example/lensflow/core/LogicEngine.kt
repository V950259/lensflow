package com.example.lensflow.core

class LogicEngine {

    // 预设的常见过敏原清单
    private val allergenList = listOf(
        "花生", "牛奶", "鸡蛋", "大豆", "小麦", "坚果", "鱼", "海鲜", "虾", "蟹", "芒果", "菠萝"
    )

    /**
     * 对比成分与过敏原清单，返回风险列表
     * @param ingredients 成分列表
     * @return 风险列表 (去重)
     */
    fun analyzeHealthRisk(ingredients: List<String>): List<String> {
        val risks = mutableSetOf<String>()

        if (ingredients.isEmpty()) {
            return emptyList()
        }

        for (ingredient in ingredients) {
            for (allergen in allergenList) {
                if (ingredient.contains(allergen, ignoreCase = true)) {
                    risks.add(allergen)
                }
            }
        }

        return risks.toList()
    }
}
