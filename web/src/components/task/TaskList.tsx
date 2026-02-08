import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import {
  useListTasksTasksGet,
  useDeleteTaskTasksTaskIdDelete,
  getListTasksTasksGetQueryKey,
} from "../../api/generated";
import { TaskItem } from "./TaskItem";

export function TaskList() {
  const [order, setOrder] = useState<"asc" | "desc">("desc");
  const queryClient = useQueryClient();
  const { data, isLoading, error } = useListTasksTasksGet({ order });
  const deleteMutation = useDeleteTaskTasksTaskIdDelete({
    mutation: {
      onSuccess: () => {
        queryClient.invalidateQueries({
          queryKey: getListTasksTasksGetQueryKey(),
        });
      },
    },
  });

  const handleDelete = (id: number) => {
    deleteMutation.mutate({ taskId: id });
  };

  const toggleOrder = () => {
    setOrder((prev) => (prev === "desc" ? "asc" : "desc"));
  };

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

  const { tasks } = data;

  if (tasks.length === 0) {
    return (
      <div className="text-center py-12 text-base-content/50">
        タスクがありません。新規作成してください。
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="table">
        <thead>
          <tr>
            <th>タイトル</th>
            <th>内容</th>
            <th>
              <button
                className="btn btn-ghost btn-xs gap-1"
                onClick={toggleOrder}
              >
                締切日 {order === "desc" ? "↓" : "↑"}
              </button>
            </th>
            <th />
          </tr>
        </thead>
        <tbody>
          {tasks.map((task) => (
            <TaskItem key={task.id} task={task} onDelete={handleDelete} />
          ))}
        </tbody>
      </table>
    </div>
  );
}
