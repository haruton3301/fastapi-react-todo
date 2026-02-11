import type { StatusResponse } from "../../api/generated";
import { StatusItem } from "./StatusItem";

type Props = {
  statuses: StatusResponse[];
  onDelete: (id: number) => void;
  onReorder: (order: number[]) => void;
};

export function StatusList({ statuses, onDelete, onReorder }: Props) {
  if (statuses.length === 0) {
    return (
      <div className="text-center py-12 text-base-content/50">
        ステータスがありません。新規作成してください。
      </div>
    );
  }

  const handleMoveUp = (index: number) => {
    const ids = statuses.map((s) => s.id);
    [ids[index - 1], ids[index]] = [ids[index], ids[index - 1]];
    onReorder(ids);
  };

  const handleMoveDown = (index: number) => {
    const ids = statuses.map((s) => s.id);
    [ids[index], ids[index + 1]] = [ids[index + 1], ids[index]];
    onReorder(ids);
  };

  return (
    <div className="overflow-x-auto">
      <table className="table">
        <thead>
          <tr>
            <th>名前</th>
            <th>カラー</th>
            <th>順序</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {statuses.map((status, index) => (
            <StatusItem
              key={status.id}
              status={status}
              onDelete={onDelete}
              onMoveUp={index > 0 ? () => handleMoveUp(index) : undefined}
              onMoveDown={
                index < statuses.length - 1
                  ? () => handleMoveDown(index)
                  : undefined
              }
            />
          ))}
        </tbody>
      </table>
    </div>
  );
}
