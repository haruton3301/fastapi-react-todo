import type { TaskResponse, StatusResponse, SortOrder } from "../../api/generated";
import { TaskItem } from "./TaskItem";

type Props = {
  tasks: TaskResponse[];
  statusMap: Map<number, StatusResponse>;
  order: SortOrder;
  onToggleOrder: () => void;
  onDelete: (id: number) => void;
};

export function TaskList({ tasks, statusMap, order, onToggleOrder, onDelete }: Props) {
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
            <th>ステータス</th>
            <th>
              <button
                className="btn btn-ghost btn-xs gap-1"
                onClick={onToggleOrder}
              >
                締切日 {order === "desc" ? "↓" : "↑"}
              </button>
            </th>
            <th />
          </tr>
        </thead>
        <tbody>
          {tasks.map((task) => (
            <TaskItem key={task.id} task={task} status={statusMap.get(task.status_id)} onDelete={onDelete} />
          ))}
        </tbody>
      </table>
    </div>
  );
}
