const taskDetailMap: Record<string, string> = {
  "Task deadline has passed": "已超过截止时间，无法提交",
  "Submission deadline has passed": "已超过截止时间，无法提交",
  "Deadline has passed": "已超过截止时间，无法提交",
  "The deadline has passed": "已超过截止时间，无法提交",
  "Submission is closed": "已超过截止时间，无法提交",
  "Task is closed": "已超过截止时间，无法提交",
};

const hasChinese = (text?: string) => Boolean(text && /[\u4e00-\u9fff]/.test(text));

export const translateTaskDetail = (detail?: string) => {
  if (!detail) return "";
  if (hasChinese(detail)) return detail;
  const trimmed = detail.trim();
  if (taskDetailMap[trimmed]) return taskDetailMap[trimmed];
  const lower = trimmed.toLowerCase();
  const hitDeadline = lower.includes("deadline");
  const hitExpired =
    lower.includes("expired") ||
    lower.includes("overdue") ||
    lower.includes("passed") ||
    lower.includes("late") ||
    lower.includes("closed");
  if (hitDeadline && hitExpired) {
    return "已超过截止时间，无法提交";
  }
  if (lower.includes("submission") && hitExpired) {
    return "已超过截止时间，无法提交";
  }
  return "";
};
