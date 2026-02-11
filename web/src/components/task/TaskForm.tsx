import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import type { z } from "zod";
import { CreateTaskTasksPostBody } from "../../api/schemas";
import {
  useListStatusesStatusesGet,
  type StatusResponse,
} from "../../api/generated";

type TaskFormValues = z.infer<typeof CreateTaskTasksPostBody>;

type Props = {
  defaultValues?: TaskFormValues;
  onSubmit: (values: TaskFormValues) => void;
  isPending: boolean;
};

export function TaskForm({ defaultValues, onSubmit, isPending }: Props) {
  const { data: statusData } = useListStatusesStatusesGet();
  const statuses: StatusResponse[] = statusData?.statuses ?? [];

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<TaskFormValues>({
    resolver: zodResolver(CreateTaskTasksPostBody),
    defaultValues: defaultValues ?? {
      title: "",
      content: "",
      due_date: "",
      status_id: statuses[0]?.id ?? 0,
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
      <fieldset className="fieldset">
        <label className="fieldset-label" htmlFor="title">
          タイトル
        </label>
        <input
          id="title"
          type="text"
          className={`input input-bordered w-full ${errors.title ? "input-error" : ""}`}
          {...register("title")}
        />
        {errors.title && (
          <p className="text-error text-sm mt-1">{errors.title.message}</p>
        )}
      </fieldset>

      <fieldset className="fieldset">
        <label className="fieldset-label" htmlFor="content">
          内容
        </label>
        <textarea
          id="content"
          className={`textarea textarea-bordered w-full ${errors.content ? "textarea-error" : ""}`}
          rows={4}
          {...register("content")}
        />
        {errors.content && (
          <p className="text-error text-sm mt-1">{errors.content.message}</p>
        )}
      </fieldset>

      <fieldset className="fieldset">
        <label className="fieldset-label" htmlFor="due_date">
          締切日
        </label>
        <input
          id="due_date"
          type="date"
          className={`input input-bordered w-full ${errors.due_date ? "input-error" : ""}`}
          {...register("due_date")}
        />
        {errors.due_date && (
          <p className="text-error text-sm mt-1">{errors.due_date.message}</p>
        )}
      </fieldset>

      <fieldset className="fieldset">
        <label className="fieldset-label" htmlFor="status_id">
          ステータス
        </label>
        <select
          id="status_id"
          className={`select select-bordered w-full ${errors.status_id ? "select-error" : ""}`}
          {...register("status_id", { valueAsNumber: true })}
        >
          {statuses.map((s) => (
            <option key={s.id} value={s.id}>
              {s.name}
            </option>
          ))}
        </select>
        {errors.status_id && (
          <p className="text-error text-sm mt-1">{errors.status_id.message}</p>
        )}
      </fieldset>

      <button type="submit" className="btn btn-primary" disabled={isPending}>
        {isPending && <span className="loading loading-spinner loading-sm" />}
        保存
      </button>
    </form>
  );
}
