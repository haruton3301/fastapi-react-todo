import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useSignupAuthSignupPost, type UserCreate } from "../../api/generated";
import { SignupAuthSignupPostBody } from "../../api/schemas";

export const Route = createFileRoute("/_auth/signup")({
  component: Signup,
});

function Signup() {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<UserCreate>({
    resolver: zodResolver(SignupAuthSignupPostBody),
  });

  const signupMutation = useSignupAuthSignupPost({
    mutation: {
      onSuccess: () => {
        navigate({ to: "/login" });
      },
      onError: (err: unknown) => {
        const message = err instanceof Error ? err.message : "";
        if (message.includes("409")) {
          setError("このユーザー名またはメールアドレスは既に使用されています");
        } else {
          setError("登録に失敗しました");
        }
      },
    },
  });

  const onSubmit = (values: UserCreate) => {
    setError(null);
    signupMutation.mutate({ data: values });
  };

  return (
    <div className="max-w-md mx-auto">
      <h2 className="text-2xl font-bold mb-4">新規登録</h2>
      {error && (
        <div className="alert alert-error mb-4">
          <span>{error}</span>
        </div>
      )}
      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
        <label className="floating-label">
          <span>ユーザー名</span>
          <input
            type="text"
            placeholder="ユーザー名"
            className="input input-bordered w-full"
            {...register("username")}
          />
          {errors.username && (
            <span className="text-error text-sm">{errors.username.message}</span>
          )}
        </label>
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
        <label className="floating-label">
          <span>パスワード</span>
          <input
            type="password"
            placeholder="パスワード"
            className="input input-bordered w-full"
            {...register("password")}
          />
          {errors.password && (
            <span className="text-error text-sm">{errors.password.message}</span>
          )}
        </label>
        <button
          type="submit"
          className="btn btn-primary"
          disabled={isSubmitting || signupMutation.isPending}
        >
          {signupMutation.isPending ? (
            <span className="loading loading-spinner loading-sm" />
          ) : (
            "登録"
          )}
        </button>
      </form>
      <p className="mt-4 text-center">
        既にアカウントをお持ちの方は{" "}
        <Link to="/login" className="link link-primary">
          ログイン
        </Link>
      </p>
    </div>
  );
}
