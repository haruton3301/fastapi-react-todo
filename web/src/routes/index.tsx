import { useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { useQueryClient } from "@tanstack/react-query";
import {
  useListTasksTasksGet,
  useDeleteTaskTasksTaskIdDelete,
  getListTasksTasksGetQueryKey,
  type SortOrder,
} from "../api/generated";
import { TaskList } from "../components/task/TaskList";
import { myToast } from "../lib/toast";

export const Route = createFileRoute("/")({
  component: Index,
});

function Index() {
  const [order, setOrder] = useState<SortOrder>("desc");
  const queryClient = useQueryClient();
  const { data, isLoading, error } = useListTasksTasksGet({ order });
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
      order={order}
      onToggleOrder={() => setOrder((prev) => (prev === "desc" ? "asc" : "desc"))}
      onDelete={(id) => deleteMutation.mutate({ taskId: id })}
    />
  );
}
