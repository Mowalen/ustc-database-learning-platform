import dayjs from "dayjs";

export function formatDate(value?: string | null, pattern = "YYYY年MM月DD日 HH:mm") {
  if (!value) return "-";
  return dayjs(value).format(pattern);
}

export function formatRole(roleId?: number | null) {
  switch (roleId) {
    case 1:
      return "学生";
    case 2:
      return "教师";
    case 3:
      return "管理员";
    default:
      return "未知";
  }
}

export function formatTaskType(type?: string | null) {
  if (!type) return "-";
  return type === "exam" ? "考试" : "作业";
}

export function formatStatus(status?: string | null) {
  if (!status) return "-";
  const map: Record<string, string> = {
    submitted: "已提交",
    graded: "已评分",
    late: "迟交",
    active: "进行中",
    dropped: "已退课",
  };
  return map[status] || status;
}
