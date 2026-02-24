import { createFileRoute } from "@tanstack/react-router";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useState } from "react";
import { useRequestPasswordResetAuthPasswordResetRequestPost } from "../../api/generated";

const forgotPasswordSchema = z.object({
  email: z.email(),
});

type ForgotPasswordForm = z.infer<typeof forgotPasswordSchema>;

export const Route = createFileRoute("/_auth/forgot-password")({
  component: ForgotPassword,
});

function ForgotPassword() {
  const [submitted, setSubmitted] = useState(false);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ForgotPasswordForm>({
    resolver: zodResolver(forgotPasswordSchema),
  });

  const requestMutation = useRequestPasswordResetAuthPasswordResetRequestPost({
    mutation: {
      onSettled: () => {
        setSubmitted(true);
      },
    },
  });

  const onSubmit = (values: ForgotPasswordForm) => {
    requestMutation.mutate({ data: { email: values.email } });
  };

  if (submitted) {
    return (
      <div className="max-w-md mx-auto">
        <h2 className="text-2xl font-bold mb-4">パスワードリセット</h2>
        <div className="alert alert-success">
          <span>
            メールを送信しました。受信ボックスをご確認ください。
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto">
      <h2 className="text-2xl font-bold mb-4">パスワードリセット</h2>
      <p className="mb-4 text-base-content/70">
        登録済みのメールアドレスを入力してください。パスワードリセット用のリンクをお送りします。
      </p>
      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
        <label className="floating-label">
          <span>メールアドレス</span>
          <input
            type="email"
            placeholder="メールアドレス"
            className="input input-bordered w-full"
            {...register("email")}
          />
          {errors.email && (
            <span className="text-error text-sm">{errors.email.message}</span>
          )}
        </label>
        <button
          type="submit"
          className="btn btn-primary"
          disabled={isSubmitting || requestMutation.isPending}
        >
          {requestMutation.isPending ? (
            <span className="loading loading-spinner loading-sm" />
          ) : (
            "送信する"
          )}
        </button>
      </form>
    </div>
  );
}
