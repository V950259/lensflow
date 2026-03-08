package com.example.lensflow.core

import android.content.Context
import android.content.Intent
import android.provider.CalendarContract
import java.text.SimpleDateFormat
import java.util.Calendar
import java.util.Locale

class CalendarManager(private val context: Context) {

    /**
     * 将活动添加到 Android 系统日历
     * @param title 活动标题
     * @param timeStr 时间字符串 (格式: YYYY-MM-DD HH:MM)
     * @param location 地点
     */
    fun addEventToCalendar(title: String, timeStr: String, location: String) {
        try {
            val sdf = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault())
            val date = sdf.parse(timeStr) ?: return
            
            val startMillis = date.time
            // 默认活动持续 1 小时
            val endMillis = startMillis + 60 * 60 * 1000

            val intent = Intent(Intent.ACTION_INSERT).apply {
                data = CalendarContract.Events.CONTENT_URI
                putExtra(CalendarContract.Events.TITLE, title)
                putExtra(CalendarContract.Events.EVENT_LOCATION, location)
                putExtra(CalendarContract.EXTRA_EVENT_BEGIN_TIME, startMillis)
                putExtra(CalendarContract.EXTRA_EVENT_END_TIME, endMillis)
                putExtra(CalendarContract.Events.DESCRIPTION, "由 LensFlow 自动提取")
                // 设为非全天事件
                putExtra(CalendarContract.Events.ALL_DAY, false)
            }
            
            if (intent.resolveActivity(context.packageManager) != null) {
                context.startActivity(intent)
            } else {
                // 处理没有日历应用的情况，实际开发中可以弹Toast提示
                println("No Calendar App found")
            }

        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
}
