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
    <div>
      <div className="flex justify-end mb-2">
        <button
          className="btn btn-ghost btn-xs gap-1"
          onClick={onToggleOrder}
        >
          締切日 {order === "desc" ? "↓" : "↑"}
        </button>
      </div>
      <div className="divide-y divide-base-300">
        {tasks.map((task) => (
          <TaskItem key={task.id} task={task} status={statusMap.get(task.status_id)} onDelete={onDelete} />
        ))}
      </div>
    </div>
  );
}
