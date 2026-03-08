package com.example.lensflow

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat
import com.example.lensflow.core.CalendarManager
import com.example.lensflow.core.LogicEngine
import com.example.lensflow.ui.CameraPreview

class MainActivity : ComponentActivity() {

    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            // Permission granted
        } else {
            Toast.makeText(this, "Camera permission required", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA)
            != PackageManager.PERMISSION_GRANTED) {
            requestPermissionLauncher.launch(Manifest.permission.CAMERA)
        }

        setContent {
            LensFlowApp()
        }
    }
}

@Composable
fun LensFlowApp() {
    val context = LocalContext.current
    val logicEngine = remember { LogicEngine() }
    val calendarManager = remember { CalendarManager(context) }
    
    // 模拟数据状态
    var showOverlay by remember { mutableStateOf(true) }
    var analysisResult by remember { mutableStateOf("正在扫描...") }
    
    // 模拟演示数据
    val demoIngredients = listOf("小麦粉", "白砂糖", "植物油", "花生酱")
    val demoEvent = Triple("团队会议", "2026-02-25 14:00", "会议室 A")

    Box(modifier = Modifier.fillMaxSize()) {
        // 1. Camera Preview Layer
        CameraPreview(modifier = Modifier.fillMaxSize())

        // 2. Result Overlay Layer
        if (showOverlay) {
            ResultOverlay(
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .padding(16.dp),
                title = "检测到: 零食包装",
                description = "包含潜在过敏原",
                onActionClick = {
                    // 演示：点击按钮触发逻辑
                    val risks = logicEngine.analyzeHealthRisk(demoIngredients)
                    if (risks.isNotEmpty()) {
                        Toast.makeText(context, "警告: 包含 ${risks.joinToString()}", Toast.LENGTH_LONG).show()
                    } else {
                        Toast.makeText(context, "安全", Toast.LENGTH_SHORT).show()
                    }
                    
                    // 演示：添加日历
                    calendarManager.addEventToCalendar(demoEvent.first, demoEvent.second, demoEvent.third)
                }
            )
        }
    }
}

@Composable
fun ResultOverlay(
    modifier: Modifier = Modifier,
    title: String,
    description: String,
    onActionClick: () -> Unit
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White.copy(alpha = 0.9f))
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(text = title, fontSize = 20.sp, fontWeight = FontWeight.Bold, color = Color.Black)
            Spacer(modifier = Modifier.height(4.dp))
            Text(text = description, fontSize = 14.sp, color = Color.Gray)
            Spacer(modifier = Modifier.height(12.dp))
            Button(
                onClick = onActionClick,
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF667EEA))
            ) {
                Text("查看详情 / 添加日程")
            }
        }
    }
}
