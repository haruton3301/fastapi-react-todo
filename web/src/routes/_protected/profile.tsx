import { createFileRoute } from "@tanstack/react-router";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod/v4";
import { useUpdateMeAuthMePut } from "../../api/generated";
import { UpdateMeAuthMePutBody } from "../../api/schemas";
import { useAuthStore } from "../../store/auth";
import { myToast } from "../../lib/toast";

export const Route = createFileRoute("/_protected/profile")({
  component: Profile,
});

type FormValues = z.infer<typeof UpdateMeAuthMePutBody>;

function Profile() {
  const user = useAuthStore((s) => s.user);
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(UpdateMeAuthMePutBody),
    defaultValues: { username: user?.username ?? "" },
  });

  const mutation = useUpdateMeAuthMePut({
    mutation: {
      onSuccess: (updatedUser) => {
        useAuthStore.getState().setUser(updatedUser);
        myToast.success("ユーザー名を変更しました");
      },
      onError: (error: unknown) => {
        const status = (error as { status?: number })?.status;
        if (status === 409) {
          setError("username", { message: "このユーザー名は使用済みです" });
        } else {
          myToast.error("ユーザー名の変更に失敗しました");
        }
      },
    },
  });

  return (
    <div className="max-w-md mx-auto">
      <h2 className="text-2xl font-bold mb-6">プロフィール</h2>
      <div className="card bg-base-100 shadow-sm">
        <div className="card-body">
          <h3 className="card-title text-lg">ユーザー名の変更</h3>
          <form onSubmit={handleSubmit((values) => mutation.mutate({ data: values }))}>
            <div className="form-control mb-4">
              <label className="label">
                <span className="label-text">ユーザー名</span>
              </label>
              <input
                {...register("username")}
                type="text"
                className={`input input-bordered${errors.username ? " input-error" : ""}`}
              />
              {errors.username && (
                <span className="label-text-alt text-error mt-1">
                  {errors.username.message}
                </span>
              )}
            </div>
            <button
              type="submit"
              className="btn btn-primary w-full"
              disabled={mutation.isPending}
            >
              {mutation.isPending ? (
                <span className="loading loading-spinner loading-sm" />
              ) : (
                "変更する"
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
