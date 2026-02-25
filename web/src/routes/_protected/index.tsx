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
});

export const Route = createFileRoute("/_protected/")({
  validateSearch: searchSchema,
  component: Index,
});

function Index() {
  const { order, q } = Route.useSearch();
  const navigate = Route.useNavigate();
  const queryClient = useQueryClient();
  const { data, isLoading, isFetching, error } = useListTasksTasksGet(
    { order, q: q || undefined },
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
      {taskListContent}
    </div>
  );
}
