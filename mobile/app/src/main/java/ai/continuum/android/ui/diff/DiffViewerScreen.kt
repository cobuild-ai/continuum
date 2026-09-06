package ai.continuum.android.ui.diff

import androidx.compose.foundation.background
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.CallMerge
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import ai.continuum.android.ui.chat.ChatViewModel
import ai.continuum.android.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DiffViewerScreen(
    taskId: String,
    viewModel: ChatViewModel,
    onNavigateBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    val diffSummary by viewModel.diffSummary.collectAsState()
    val activeTask by viewModel.activeTask.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(
                            text = "📑 Diff Inspector",
                            fontWeight = FontWeight.Bold,
                            fontSize = 18.sp,
                            color = TextPrimary
                        )
                        Text(
                            text = "Branch: ${activeTask?.branchName ?: "ai/$taskId"} ➔ main",
                            fontSize = 12.sp,
                            color = PrimaryCyan
                        )
                    }
                },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back", tint = PrimaryCyan)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = SurfaceDark)
            )
        },
        bottomBar = {
            Surface(
                color = SurfaceDark,
                modifier = Modifier.fillMaxWidth().navigationBarsPadding()
            ) {
                Row(
                    modifier = Modifier.padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(
                            text = "${diffSummary?.totalFilesChanged ?: 0} files modified",
                            color = TextSecondary,
                            fontSize = 12.sp
                        )
                        Row {
                            Text(
                                text = "+${diffSummary?.totalAdditions ?: 0} ",
                                color = DiffAdditionText,
                                fontWeight = FontWeight.Bold,
                                fontSize = 13.sp
                            )
                            Text(
                                text = "-${diffSummary?.totalDeletions ?: 0}",
                                color = DiffDeletionText,
                                fontWeight = FontWeight.Bold,
                                fontSize = 13.sp
                            )
                        }
                    }

                    Button(
                        onClick = {
                            viewModel.approveSquashMerge(taskId) {
                                onNavigateBack()
                            }
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = PassGreen),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Icon(Icons.AutoMirrored.Filled.CallMerge, contentDescription = null, tint = BackgroundDark)
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = "One-Touch Squash Merge",
                            color = BackgroundDark,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
            }
        },
        containerColor = BackgroundDark,
        modifier = modifier.fillMaxSize()
    ) { paddingValues ->
        val files = diffSummary?.files ?: emptyList()

        if (files.isEmpty()) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues),
                contentAlignment = Alignment.Center
            ) {
                Text("No changes detected in sandbox.", color = TextMuted)
            }
        } else {
            LazyColumn(
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp),
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues)
            ) {
                items(files) { fileDiff ->
                    Card(
                        shape = RoundedCornerShape(12.dp),
                        colors = CardDefaults.cardColors(containerColor = SurfaceDark),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Column(modifier = Modifier.padding(12.dp)) {
                            // File header
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.SpaceBetween,
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                Text(
                                    text = fileDiff.filepath,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 14.sp,
                                    fontFamily = FontFamily.Monospace,
                                    color = PrimaryCyan
                                )
                                Text(
                                    text = "+${fileDiff.additions} -${fileDiff.deletions}",
                                    fontSize = 12.sp,
                                    color = TextSecondary
                                )
                            }

                            Spacer(modifier = Modifier.height(8.dp))

                            // Diff content with horizontal scrolling
                            val horizontalScroll = rememberScrollState()
                            Column(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .background(BackgroundDark, RoundedCornerShape(8.dp))
                                    .padding(8.dp)
                                    .horizontalScroll(horizontalScroll)
                            ) {
                                val lines = fileDiff.patch.split("\n")
                                lines.forEach { line ->
                                    val (bgColor, textColor) = when {
                                        line.startsWith("+") && !line.startsWith("+++") -> DiffAdditionBg to DiffAdditionText
                                        line.startsWith("-") && !line.startsWith("---") -> DiffDeletionBg to DiffDeletionText
                                        line.startsWith("@@") -> Color(0xFF1E1B4B) to SecondaryBlue
                                        else -> Color.Transparent to TextSecondary
                                    }

                                    Box(
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .background(bgColor)
                                            .padding(horizontal = 4.dp, vertical = 1.dp)
                                    ) {
                                        Text(
                                            text = line,
                                            fontFamily = FontFamily.Monospace,
                                            fontSize = 12.sp,
                                            color = textColor
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
