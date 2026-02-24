import * as z from "zod";

z.config({
  ...z.locales.ja(),
  customError: (iss) => {
    if (iss.code === "too_small" && iss.minimum === 1) {
      return "必須項目です";
    }
    if (iss.code === "invalid_format" && iss.format === "date") {
      return "正しい日付形式で入力してください";
    }
    if (iss.code === "invalid_type" && iss.expected === "number" && iss.path?.includes("status_id")) {
      return "ステータスを選択してください";
    }
  },
});
