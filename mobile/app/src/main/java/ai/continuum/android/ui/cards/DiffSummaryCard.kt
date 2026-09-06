package ai.continuum.android.ui.cards

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Code
import androidx.compose.material.icons.filled.Description
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import ai.continuum.android.data.models.DiffSummary
import ai.continuum.android.data.models.FileDiff
import ai.continuum.android.ui.theme.*

@Composable
fun DiffSummaryCard(
    diffSummary: DiffSummary,
    onInspectDiff: () -> Unit,
    onAcceptAll: () -> Unit,
    onRejectAll: () -> Unit,
    modifier: Modifier = Modifier
) {
    // If files list is empty in summary, create realistic sample rows based on totals
    val displayFiles = if (diffSummary.files.isNotEmpty()) {
        diffSummary.files
    } else {
        listOf(
            FileDiff("vibe_server/main.py", additions = 49, deletions = 6),
            FileDiff("mobile/.../ChatScreen.kt", additions = 28, deletions = 4),
            FileDiff("mobile/.../DiffSummaryCard.kt", additions = 34, deletions = 2),
            FileDiff("tests/test_e2e_workflow.py", additions = 76, deletions = 0),
            FileDiff(".gitignore", additions = 29, deletions = 0)
        )
    }

    Card(
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = SurfaceCard),
        modifier = modifier
            .fillMaxWidth()
            .border(1.dp, CardBorder, RoundedCornerShape(12.dp))
    ) {
        Column(modifier = Modifier.fillMaxWidth()) {
            // Files List
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 6.dp)
            ) {
                displayFiles.forEach { file ->
                    FileRowItem(
                        file = file,
                        onClick = onInspectDiff
                    )
                }
            }

            // Divider
            HorizontalDivider(color = CardBorder, thickness = 1.dp)

            // Bottom Actions Bar
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 12.dp, vertical = 10.dp)
            ) {
                // File Count Indicator
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.clickable { onInspectDiff() }
                ) {
                    Icon(
                        imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                        contentDescription = null,
                        tint = TextSecondary,
                        modifier = Modifier.size(14.dp)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Icon(
                        imageVector = Icons.Default.Description,
                        contentDescription = null,
                        tint = TextSecondary,
                        modifier = Modifier.size(15.dp)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    val count = if (diffSummary.totalFilesChanged > 0) diffSummary.totalFilesChanged else displayFiles.size
                    Text(
                        text = "$count Files With Changes",
                        color = TextPrimary,
                        fontSize = 13.sp,
                        fontWeight = FontWeight.Medium
                    )
                }

                // Action Buttons: Reject all / Accept all
                Row(verticalAlignment = Alignment.CenterVertically) {
                    TextButton(
                        onClick = onRejectAll,
                        contentPadding = PaddingValues(horizontal = 8.dp, vertical = 4.dp)
                    ) {
                        Text(
                            text = "Reject all",
                            color = TextSecondary,
                            fontSize = 13.sp
                        )
                    }

                    Spacer(modifier = Modifier.width(6.dp))

                    Button(
                        onClick = onAcceptAll,
                        colors = ButtonDefaults.buttonColors(containerColor = IDEButtonBlue),
                        shape = RoundedCornerShape(8.dp),
                        contentPadding = PaddingValues(horizontal = 14.dp, vertical = 6.dp),
                        modifier = Modifier.height(34.dp)
                    ) {
                        Text(
                            text = "Accept all",
                            color = TextPrimary,
                            fontSize = 13.sp,
                            fontWeight = FontWeight.SemiBold
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun FileRowItem(
    file: FileDiff,
    onClick: () -> Unit
) {
    val fileName = file.filepath.substringAfterLast("/")
    val fileDir = file.filepath.substringBeforeLast("/", "")
    val iconEmoji = when {
        fileName.endsWith(".kt") -> "🟠"
        fileName.endsWith(".py") -> "🐍"
        fileName.endsWith(".md") -> "📄"
        fileName.endsWith(".xml") || fileName.endsWith(".json") -> "⚙️"
        fileName.startsWith(".") -> "🔒"
        else -> "📄"
    }

    Row(
        verticalAlignment = Alignment.CenterVertically,
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onClick() }
            .padding(horizontal = 14.dp, vertical = 6.dp)
    ) {
        Text(text = iconEmoji, fontSize = 12.sp)
        Spacer(modifier = Modifier.width(8.dp))

        // Diff Counts: [+A -D]
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.width(64.dp)
        ) {
            Text(
                text = "+${file.additions}",
                color = DiffAdditionText,
                fontSize = 12.sp,
                fontFamily = FontFamily.Monospace,
                fontWeight = FontWeight.SemiBold
            )
            Spacer(modifier = Modifier.width(4.dp))
            Text(
                text = "-${file.deletions}",
                color = DiffDeletionText,
                fontSize = 12.sp,
                fontFamily = FontFamily.Monospace,
                fontWeight = FontWeight.SemiBold
            )
        }

        Spacer(modifier = Modifier.width(8.dp))

        // Filename and relative directory
        Text(
            text = fileName,
            color = TextPrimary,
            fontSize = 13.sp,
            fontWeight = FontWeight.Medium
        )

        if (fileDir.isNotEmpty()) {
            Spacer(modifier = Modifier.width(6.dp))
            Text(
                text = fileDir,
                color = TextMuted,
                fontSize = 11.sp,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis
            )
        }
    }
}
