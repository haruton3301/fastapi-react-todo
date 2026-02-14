import { createFileRoute, Link } from "@tanstack/react-router";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useState } from "react";
import { setToken } from "../../lib/auth";
import { useLoginAuthLoginPost } from "../../api/generated";

const loginSchema = z.object({
  email: z.email(),
  password: z.string().min(1),
});

type LoginForm = z.infer<typeof loginSchema>;

export const Route = createFileRoute("/_auth/login")({
  component: Login,
});

function Login() {
  const [error, setError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });

  const loginMutation = useLoginAuthLoginPost({
    mutation: {
      onSuccess: (data) => {
        setToken(data.access_token);
        window.location.href = "/";
      },
      onError: () => {
        setError("メールアドレスまたはパスワードが正しくありません");
      },
    },
  });

  const onSubmit = (values: LoginForm) => {
    setError(null);
    loginMutation.mutate({
      data: { username: values.email, password: values.password },
    });
  };

  return (
    <div className="max-w-md mx-auto">
      <h2 className="text-2xl font-bold mb-4">ログイン</h2>
      {error && (
        <div className="alert alert-error mb-4">
          <span>{error}</span>
        </div>
      )}
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
          disabled={isSubmitting || loginMutation.isPending}
        >
          {loginMutation.isPending ? (
            <span className="loading loading-spinner loading-sm" />
          ) : (
            "ログイン"
          )}
        </button>
      </form>
      <p className="mt-4 text-center">
        アカウントをお持ちでない方は{" "}
        <Link to="/signup" className="link link-primary">
          新規登録
        </Link>
      </p>
    </div>
  );
}
