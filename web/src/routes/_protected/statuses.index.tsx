import { createFileRoute, Link } from "@tanstack/react-router";
import { useQueryClient } from "@tanstack/react-query";
import {
  useListStatusesStatusesGet,
  useDeleteStatusStatusesStatusIdDelete,
  useReorderStatusesStatusesReorderPut,
  getListStatusesStatusesGetQueryKey,
} from "../../api/generated";
import { StatusList } from "../../components/status/StatusList";
import { myToast } from "../../lib/toast";

export const Route = createFileRoute("/_protected/statuses/")({
  component: StatusIndex,
});

function StatusIndex() {
  const queryClient = useQueryClient();
  const { data, isLoading, error } = useListStatusesStatusesGet();

  const deleteMutation = useDeleteStatusStatusesStatusIdDelete({
    mutation: {
      onSuccess: () => {
        queryClient.invalidateQueries({
          queryKey: getListStatusesStatusesGetQueryKey(),
        });
        myToast.success("ステータスを削除しました");
      },
      onError: (err) => {
        if (err instanceof Error && err.message.includes("409")) {
          myToast.error(
            "このステータスに紐付くタスクが存在するため削除できません",
          );
        } else {
          myToast.error("ステータスの削除に失敗しました");
        }
      },
    },
  });

  const reorderMutation = useReorderStatusesStatusesReorderPut({
    mutation: {
      onError: () => {
        myToast.error("並び替えに失敗しました");
      },
      onSettled: () => {
        queryClient.invalidateQueries({
          queryKey: getListStatusesStatusesGetQueryKey(),
        });
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
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">ステータス管理</h2>
        <Link to="/statuses/new" className="btn btn-primary btn-sm">
          新規作成
        </Link>
      </div>
      <StatusList
        statuses={data.statuses}
        onDelete={(id) => deleteMutation.mutate({ statusId: id })}
        onReorder={(order) => reorderMutation.mutate({ data: { order } })}
      />
    </div>
  );
}
