import { createFileRoute } from "@tanstack/react-router";
import { useQueryClient } from "@tanstack/react-query";
import {
  useGetTaskTasksTaskIdGet,
  useUpdateTaskTasksTaskIdPut,
  getListTasksTasksGetQueryKey,
} from "../../api/generated";
import { TaskForm } from "../../components/task/TaskForm";
import { myToast } from "../../lib/toast";
import { useBackWithFallback } from "../../lib/navigation";

export const Route = createFileRoute("/_protected/tasks/$taskId/edit")({
  component: TaskEdit,
});

function TaskEdit() {
  const { taskId } = Route.useParams();
  const back = useBackWithFallback("/");
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useGetTaskTasksTaskIdGet(Number(taskId));
  const mutation = useUpdateTaskTasksTaskIdPut({
    mutation: {
      onSuccess: () => {
        queryClient.invalidateQueries({
          queryKey: getListTasksTasksGetQueryKey(),
        });
        myToast.success("タスクを更新しました");
        back();
      },
      onError: () => {
        myToast.error("タスクの更新に失敗しました");
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
    <div className="max-w-lg mx-auto">
      <h2 className="text-2xl font-bold mb-4">タスク編集</h2>
      <TaskForm
        defaultValues={{
          title: data.title,
          content: data.content,
          due_date: data.due_date,
          status_id: data.status_id,
        }}
        onSubmit={(values) =>
          mutation.mutate({ taskId: Number(taskId), data: values })
        }
        isPending={mutation.isPending}
      />
    </div>
  );
}
