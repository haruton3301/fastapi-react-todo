import type { TaskResponse, SortOrder } from "../../api/generated";
import { TaskItem } from "./TaskItem";

type Props = {
  tasks: TaskResponse[];
  order: SortOrder;
  onToggleOrder: () => void;
  onDelete: (id: number) => void;
};

export function TaskList({ tasks, order, onToggleOrder, onDelete }: Props) {
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
            <TaskItem key={task.id} task={task} onDelete={onDelete} />
          ))}
        </tbody>
      </table>
    </div>
  );
}
