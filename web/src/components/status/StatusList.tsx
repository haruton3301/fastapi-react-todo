import { useEffect, useState } from "react";
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import type { StatusResponse } from "../../api/generated";
import { SortableStatusItem } from "./StatusItem";

type Props = {
  statuses: StatusResponse[];
  onDelete: (id: number) => void;
  onReorder: (order: number[]) => void;
};

export function StatusList({ statuses, onDelete, onReorder }: Props) {
  const [items, setItems] = useState(statuses);

  useEffect(() => {
    setItems(statuses);
  }, [statuses]);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    }),
  );

  if (items.length === 0) {
    return (
      <div className="text-center py-12 text-base-content/50">
        ステータスがありません。新規作成してください。
      </div>
    );
  }

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over || active.id === over.id) return;

    const oldIndex = items.findIndex((s) => s.id === active.id);
    const newIndex = items.findIndex((s) => s.id === over.id);
    const newItems = arrayMove(items, oldIndex, newIndex);
    setItems(newItems);
    onReorder(newItems.map((s) => s.id));
  };

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragEnd={handleDragEnd}
    >
      <SortableContext
        items={items.map((s) => s.id)}
        strategy={verticalListSortingStrategy}
      >
        <div className="overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th className="w-8" />
                <th>名前</th>
                <th>カラー</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {items.map((status) => (
                <SortableStatusItem
                  key={status.id}
                  status={status}
                  onDelete={onDelete}
                />
              ))}
            </tbody>
          </table>
        </div>
      </SortableContext>
    </DndContext>
  );
}
