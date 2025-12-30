const authDetailMap: Record<string, string> = {
  "Incorrect username or password": "用户名或密码错误",
  "Inactive user": "账号已停用",
  "The user with this username already exists in the system": "用户名已被注册",
  "Email not found": "邮箱未找到",
  "Invalid or expired code": "验证码无效或已过期",
  "Failed to send verification email. Please try again later.": "验证码发送失败，请稍后再试",
  "The user with this email already exists in the system": "该邮箱已被注册",
};

const fieldLabels: Record<string, string> = {
  username: "用户名",
  password: "密码",
  email: "邮箱",
  full_name: "姓名",
  role_id: "角色",
};

const hasChinese = (text?: string) => Boolean(text && /[\u4e00-\u9fff]/.test(text));

const translateValidationMessage = (message?: string) => {
  if (!message) return "输入不合法";
  if (hasChinese(message)) return message;
  const lower = message.toLowerCase();
  if (lower.includes("field required") || lower.includes("missing")) return "不能为空";
  if (lower.includes("valid email")) return "邮箱格式不正确";
  const minMatch = message.match(/at least (\d+) characters?/i);
  if (minMatch) return `至少 ${minMatch[1]} 位字符`;
  const maxMatch = message.match(/at most (\d+) characters?/i);
  if (maxMatch) return `不能超过 ${maxMatch[1]} 位字符`;
  return "输入不合法";
};

export const translateAuthDetail = (detail?: string) => {
  if (!detail) return "";
  if (hasChinese(detail)) return detail;
  return authDetailMap[detail] || "";
};

export const formatValidationError = (detail: unknown) => {
  if (!Array.isArray(detail)) {
    return "";
  }
  const messages = detail.map((item) => {
    const loc = Array.isArray(item?.loc) ? item.loc : [];
    const fieldKey = loc.slice(1).join(".") || "字段";
    const label = fieldLabels[fieldKey] || fieldKey;
    const msg = translateValidationMessage(item?.msg);
    return `${label}：${msg}`;
  });
  return messages.join("；");
};
