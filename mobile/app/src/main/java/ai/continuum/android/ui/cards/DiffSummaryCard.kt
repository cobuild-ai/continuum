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
import ai.continuum.android.data.models.LensReport
import ai.continuum.android.data.models.VerificationReport
import ai.continuum.android.ui.theme.*

@Composable
fun DiffSummaryCard(
    diffSummary: DiffSummary,
    onInspectDiff: () -> Unit,
    onAcceptAll: () -> Unit,
    onRejectAll: () -> Unit,
    verificationReport: VerificationReport? = null,
    lensReport: LensReport? = null,
    isActionable: Boolean = true,
    modifier: Modifier = Modifier
) {
    val displayFiles = diffSummary.files

    Card(
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = SurfaceCard),
        modifier = modifier
            .fillMaxWidth()
            .border(1.dp, CardBorder, RoundedCornerShape(12.dp))
    ) {
        Column(modifier = Modifier.fillMaxWidth()) {
            // 5-Lens Quality Guardrail Alert Banner
            if (lensReport != null) {
                val avgScore = lensReport.averageScore
                val isLowScore = avgScore < 70.0
                val hasFailures = !lensReport.overallPassed
                if (isLowScore || hasFailures) {
                    val alertText = if (isLowScore) {
                        "Quality Guardrail Alert: 5-Lens score is ${avgScore.toInt()}/100 (< 70). Review findings before merging."
                    } else {
                        "Quality Guardrail Alert: 5-Lens audit contains failed checks (${avgScore.toInt()}/100). Review findings before merging."
                    }
                    Surface(
                        color = WarningYellow.copy(alpha = 0.12f),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            modifier = Modifier.padding(horizontal = 12.dp, vertical = 7.dp)
                        ) {
                            Text(text = "🛡️", fontSize = 13.sp)
                            Spacer(modifier = Modifier.width(6.dp))
                            Text(
                                text = alertText,
                                color = WarningYellow,
                                fontSize = 11.sp,
                                fontWeight = FontWeight.SemiBold
                            )
                        }
                    }
                    HorizontalDivider(color = CardBorder, thickness = 1.dp)
                }
            }

            // Verification Report Banner
            if (verificationReport != null) {
                val isSuccess = verificationReport.testsPassed || verificationReport.verified
                val bgColor = if (isSuccess) PassGreen.copy(alpha = 0.12f) else if (verificationReport.failedTests > 0) FailRed.copy(alpha = 0.12f) else SurfaceDark
                val textColor = if (isSuccess) PassGreen else if (verificationReport.failedTests > 0) FailRed else TextPrimary

                Surface(
                    color = bgColor,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp)
                    ) {
                        val iconEmoji = if (isSuccess) "🧪" else if (verificationReport.failedTests > 0) "⚠️" else "⚙️"
                        Text(text = iconEmoji, fontSize = 14.sp)
                        Spacer(modifier = Modifier.width(8.dp))
                        Column(modifier = Modifier.weight(1f)) {
                            val title = if (verificationReport.totalTests > 0) {
                                if (verificationReport.testsPassed) {
                                    "Tests: ${verificationReport.passedTests}/${verificationReport.totalTests} Passed (100%)"
                                } else {
                                    "Tests: ${verificationReport.failedTests} Failed (${verificationReport.passedTests}/${verificationReport.totalTests})"
                                }
                            } else {
                                if (verificationReport.verified) "Autonomous Verification Passed" else "Agent Verification Completed"
                            }

                            Text(
                                text = title,
                                color = textColor,
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Bold
                            )

                            val detailText = if (verificationReport.commandRun.isNotEmpty()) {
                                "${verificationReport.commandRun} • ${verificationReport.iterations} Turn(s)"
                            } else if (verificationReport.summary.isNotEmpty()) {
                                verificationReport.summary
                            } else {
                                ""
                            }
                            if (detailText.isNotEmpty()) {
                                Text(
                                    text = detailText,
                                    color = TextSecondary,
                                    fontSize = 11.sp,
                                    fontFamily = FontFamily.Monospace,
                                    maxLines = 1,
                                    overflow = TextOverflow.Ellipsis
                                )
                            }
                        }
                    }
                }
                HorizontalDivider(color = CardBorder, thickness = 1.dp)
            }

            // Files List
            if (displayFiles.isNotEmpty()) {
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
            } else {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 16.dp, horizontal = 12.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = "Working tree clean (0 files changed)",
                        color = TextSecondary,
                        fontSize = 12.sp,
                        fontFamily = FontFamily.Monospace
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
                    .padding(horizontal = 10.dp, vertical = 8.dp)
            ) {
                // File Count Indicator
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier
                        .weight(1f)
                        .clickable { onInspectDiff() }
                ) {
                    Icon(
                        imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                        contentDescription = null,
                        tint = TextSecondary,
                        modifier = Modifier.size(13.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Icon(
                        imageVector = Icons.Default.Description,
                        contentDescription = null,
                        tint = TextSecondary,
                        modifier = Modifier.size(14.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    val count = if (diffSummary.totalFilesChanged > 0) diffSummary.totalFilesChanged else displayFiles.size
                    Text(
                        text = "$count Files Changed",
                        color = TextPrimary,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Medium,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                }

                // Action Buttons: Reject / Accept all (only when isActionable)
                if (isActionable) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.End
                    ) {
                        TextButton(
                            onClick = onRejectAll,
                            contentPadding = PaddingValues(horizontal = 6.dp, vertical = 2.dp)
                        ) {
                            Text(
                                text = "Reject",
                                color = TextSecondary,
                                fontSize = 12.sp
                            )
                        }

                        Spacer(modifier = Modifier.width(4.dp))

                        Button(
                            onClick = onAcceptAll,
                            colors = ButtonDefaults.buttonColors(containerColor = IDEButtonBlue),
                            shape = RoundedCornerShape(8.dp),
                            contentPadding = PaddingValues(horizontal = 12.dp, vertical = 4.dp),
                            modifier = Modifier.height(32.dp)
                        ) {
                            Text(
                                text = "Accept all",
                                color = TextPrimary,
                                fontSize = 12.sp,
                                fontWeight = FontWeight.SemiBold
                            )
                        }
                    }
                } else {
                    Text(
                        text = "✓ Merged",
                        color = PassGreen,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.SemiBold,
                        modifier = Modifier.padding(end = 4.dp)
                    )
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
