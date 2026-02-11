import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useQueryClient } from "@tanstack/react-query";
import {
  useGetStatusStatusesStatusIdGet,
  useUpdateStatusStatusesStatusIdPut,
  getListStatusesStatusesGetQueryKey,
} from "../api/generated";
import { StatusForm } from "../components/status/StatusForm";
import { myToast } from "../lib/toast";

export const Route = createFileRoute("/statuses/$statusId/edit")({
  component: StatusEdit,
});

function StatusEdit() {
  const { statusId } = Route.useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useGetStatusStatusesStatusIdGet(
    Number(statusId),
  );
  const mutation = useUpdateStatusStatusesStatusIdPut({
    mutation: {
      onSuccess: () => {
        queryClient.invalidateQueries({
          queryKey: getListStatusesStatusesGetQueryKey(),
        });
        myToast.success("ステータスを更新しました");
        navigate({ to: "/statuses" });
      },
      onError: () => {
        myToast.error("ステータスの更新に失敗しました");
      },
    },
  });

  if (isLoading) {
    return <span className="loading loading-spinner loading-md" />;
  }

  if (!data || error) {
    return (
      <div className="alert alert-error">
        <span>ステータスの読み込みに失敗しました</span>
      </div>
    );
  }

  return (
    <div className="max-w-lg mx-auto">
      <h2 className="text-2xl font-bold mb-4">ステータス編集</h2>
      <StatusForm
        defaultValues={{
          name: data.name,
          color: data.color,
        }}
        onSubmit={(values) =>
          mutation.mutate({ statusId: Number(statusId), data: values })
        }
        isPending={mutation.isPending}
      />
    </div>
  );
}
