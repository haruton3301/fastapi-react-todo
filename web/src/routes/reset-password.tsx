import { createFileRoute, useRouter } from "@tanstack/react-router";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useState } from "react";
import { useConfirmPasswordResetAuthPasswordResetConfirmPost } from "../api/generated";

const resetPasswordSchema = z
  .object({
    new_password: z.string().min(8, "パスワードは8文字以上で入力してください"),
    confirm_password: z.string().min(1),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: "パスワードが一致しません",
    path: ["confirm_password"],
  });

type ResetPasswordForm = z.infer<typeof resetPasswordSchema>;

const resetPasswordSearchSchema = z.object({
  token: z.string(),
});

export const Route = createFileRoute("/reset-password")({
  validateSearch: resetPasswordSearchSchema,
  component: ResetPassword,
});

function ResetPassword() {
  const { token } = Route.useSearch();
  const { navigate } = useRouter();
  const [error, setError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ResetPasswordForm>({
    resolver: zodResolver(resetPasswordSchema),
  });

  const confirmMutation = useConfirmPasswordResetAuthPasswordResetConfirmPost({
    mutation: {
      onSuccess: () => {
        navigate({ to: "/login" });
      },
      onError: () => {
        setError("リンクが無効または期限切れです");
      },
    },
  });

  const onSubmit = (values: ResetPasswordForm) => {
    setError(null);
    confirmMutation.mutate({
      data: { token, new_password: values.new_password },
    });
  };

  return (
    <div className="max-w-md mx-auto mt-16">
      <h2 className="text-2xl font-bold mb-4">新しいパスワードの設定</h2>
      {error && (
        <div className="alert alert-error mb-4">
          <span>{error}</span>
        </div>
      )}
      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
        <label className="floating-label">
          <span>新しいパスワード</span>
          <input
            type="password"
            placeholder="新しいパスワード（8文字以上）"
            className="input input-bordered w-full"
            {...register("new_password")}
          />
          {errors.new_password && (
            <span className="text-error text-sm">{errors.new_password.message}</span>
          )}
        </label>
        <label className="floating-label">
          <span>パスワード（確認）</span>
          <input
            type="password"
            placeholder="パスワードを再入力"
            className="input input-bordered w-full"
            {...register("confirm_password")}
          />
          {errors.confirm_password && (
            <span className="text-error text-sm">{errors.confirm_password.message}</span>
          )}
        </label>
        <button
          type="submit"
          className="btn btn-primary"
          disabled={isSubmitting || confirmMutation.isPending}
        >
          {confirmMutation.isPending ? (
            <span className="loading loading-spinner loading-sm" />
          ) : (
            "パスワードを変更する"
          )}
        </button>
      </form>
    </div>
  );
}
