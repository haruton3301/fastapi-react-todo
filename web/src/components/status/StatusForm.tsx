import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import type { z } from "zod";
import { CreateStatusStatusesPostBody } from "../../api/schemas";

type StatusFormValues = z.infer<typeof CreateStatusStatusesPostBody>;

type Props = {
  defaultValues?: StatusFormValues;
  onSubmit: (values: StatusFormValues) => void;
  isPending: boolean;
};

export function StatusForm({ defaultValues, onSubmit, isPending }: Props) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<StatusFormValues>({
    resolver: zodResolver(CreateStatusStatusesPostBody),
    defaultValues: defaultValues ?? {
      name: "",
      color: "#3b82f6",
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
      <fieldset className="fieldset">
        <label className="fieldset-label" htmlFor="name">
          名前
        </label>
        <input
          id="name"
          type="text"
          className={`input input-bordered w-full ${errors.name ? "input-error" : ""}`}
          {...register("name")}
        />
        {errors.name && (
          <p className="text-error text-sm mt-1">{errors.name.message}</p>
        )}
      </fieldset>

      <fieldset className="fieldset">
        <label className="fieldset-label" htmlFor="color">
          カラー
        </label>
        <input
          id="color"
          type="color"
          className={`input input-bordered w-full h-12 ${errors.color ? "input-error" : ""}`}
          {...register("color")}
        />
        {errors.color && (
          <p className="text-error text-sm mt-1">{errors.color.message}</p>
        )}
      </fieldset>

      <button type="submit" className="btn btn-primary" disabled={isPending}>
        {isPending && <span className="loading loading-spinner loading-sm" />}
        保存
      </button>
    </form>
  );
}
