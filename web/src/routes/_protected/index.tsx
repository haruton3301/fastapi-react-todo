import { createFileRoute } from "@tanstack/react-router";
import { keepPreviousData, useQueryClient } from "@tanstack/react-query";
import { z } from "zod";
import {
  useListTasksTasksGet,
  useListStatusesStatusesGet,
  useDeleteTaskTasksTaskIdDelete,
  getListTasksTasksGetQueryKey,
  type StatusResponse,
} from "../../api/generated";
import { TaskList } from "../../components/task/TaskList";
import { myToast } from "../../lib/toast";

const searchSchema = z.object({
  order: z.enum(["asc", "desc"]).default("desc").catch("desc"),
  q: z.string().default("").catch(""),
  due_date_from: z.string().default("").catch(""),
  due_date_to: z.string().default("").catch(""),
});

export const Route = createFileRoute("/_protected/")({
  validateSearch: searchSchema,
  component: Index,
});

function Index() {
  const { order, q, due_date_from, due_date_to } = Route.useSearch();
  const navigate = Route.useNavigate();
  const queryClient = useQueryClient();
  const { data, isLoading, isFetching, error } = useListTasksTasksGet(
    {
      order,
      q: q || undefined,
      due_date_from: due_date_from || undefined,
      due_date_to: due_date_to || undefined,
    },
    { query: { placeholderData: keepPreviousData } },
  );
  const { data: statusData } = useListStatusesStatusesGet();
  const statusMap = new Map<number, StatusResponse>(
    (statusData?.statuses ?? []).map((s) => [s.id, s]),
  );
  const deleteMutation = useDeleteTaskTasksTaskIdDelete({
    mutation: {
      onSuccess: () => {
        queryClient.invalidateQueries({
          queryKey: getListTasksTasksGetQueryKey(),
        });
        myToast.success("タスクを削除しました");
      },
      onError: () => {
        myToast.error("タスクの削除に失敗しました");
      },
    },
  });

  const taskListContent = (() => {
    if (isLoading) {
      return <span className="loading loading-spinner loading-md" />;
    }
    if (!data || error) {
      return (
        <div className="alert alert-error">
          <span>タスクの読み込みに失敗しました</span>
        </div>
      );
    }
    return (
      <TaskList
        tasks={data.tasks}
        statusMap={statusMap}
        order={order}
        onToggleOrder={() =>
          navigate({ search: (prev) => ({ ...prev, order: order === "desc" ? "asc" : "desc" }), replace: true })
        }
        onDelete={(id) => deleteMutation.mutate({ taskId: id })}
      />
    );
  })();

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-2">
        <div className="relative">
          <input
            type="text"
            placeholder="キーワードで検索..."
            className="input input-bordered w-full"
            value={q}
            onChange={(e) =>
              navigate({ search: (prev) => ({ ...prev, q: e.target.value }), replace: true })
            }
          />
          {isFetching && (
            <span className="loading loading-spinner loading-sm absolute right-3 top-1/2 -translate-y-1/2" />
          )}
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-base-content/60 shrink-0">締切日</span>
          <input
            type="date"
            className="input input-bordered input-sm"
            value={due_date_from}
            onChange={(e) =>
              navigate({ search: (prev) => ({ ...prev, due_date_from: e.target.value }), replace: true })
            }
          />
          <span className="text-sm text-base-content/60">〜</span>
          <input
            type="date"
            className="input input-bordered input-sm"
            value={due_date_to}
            min={due_date_from || undefined}
            onChange={(e) =>
              navigate({ search: (prev) => ({ ...prev, due_date_to: e.target.value }), replace: true })
            }
          />
          {(due_date_from || due_date_to) && (
            <button
              className="btn btn-ghost btn-sm"
              onClick={() =>
                navigate({ search: (prev) => ({ ...prev, due_date_from: "", due_date_to: "" }), replace: true })
              }
            >
              クリア
            </button>
          )}
        </div>
      </div>
      {taskListContent}
    </div>
  );
}
