import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useQueryClient } from "@tanstack/react-query";
import {
  useCreateTaskTasksPost,
  getListTasksTasksGetQueryKey,
} from "../../api/generated";
import { TaskForm } from "../../components/task/TaskForm";
import { myToast } from "../../lib/toast";

export const Route = createFileRoute("/_protected/tasks/new")({
  component: TaskNew,
});

function TaskNew() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const mutation = useCreateTaskTasksPost({
    mutation: {
      onSuccess: () => {
        queryClient.invalidateQueries({
          queryKey: getListTasksTasksGetQueryKey(),
        });
        myToast.success("タスクを作成しました");
        navigate({ to: "/" });
      },
      onError: () => {
        myToast.error("タスクの作成に失敗しました");
      },
    },
  });

  return (
    <div className="max-w-lg mx-auto">
      <h2 className="text-2xl font-bold mb-4">タスク作成</h2>
      <TaskForm
        onSubmit={(values) => mutation.mutate({ data: values })}
        isPending={mutation.isPending}
      />
    </div>
  );
}
