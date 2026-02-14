import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useQueryClient } from "@tanstack/react-query";
import {
  useCreateStatusStatusesPost,
  getListStatusesStatusesGetQueryKey,
} from "../../api/generated";
import { StatusForm } from "../../components/status/StatusForm";
import { myToast } from "../../lib/toast";

export const Route = createFileRoute("/_protected/statuses/new")({
  component: StatusNew,
});

function StatusNew() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const mutation = useCreateStatusStatusesPost({
    mutation: {
      onSuccess: () => {
        queryClient.invalidateQueries({
          queryKey: getListStatusesStatusesGetQueryKey(),
        });
        myToast.success("ステータスを作成しました");
        navigate({ to: "/statuses" });
      },
      onError: () => {
        myToast.error("ステータスの作成に失敗しました");
      },
    },
  });

  return (
    <div className="max-w-lg mx-auto">
      <h2 className="text-2xl font-bold mb-4">ステータス作成</h2>
      <StatusForm
        onSubmit={(values) => mutation.mutate({ data: values })}
        isPending={mutation.isPending}
      />
    </div>
  );
}
