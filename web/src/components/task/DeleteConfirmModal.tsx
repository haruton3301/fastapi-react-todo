type Props = {
  title: string;
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
};

export function DeleteConfirmModal({
  title,
  isOpen,
  onClose,
  onConfirm,
}: Props) {
  return (
    <dialog className={`modal duration-100 ${isOpen ? "modal-open" : ""}`}>
      <div className="modal-box">
        <h3 className="font-bold text-lg">削除の確認</h3>
        <p className="py-4">
          「{title}」を削除しますか？この操作は取り消せません。
        </p>
        <div className="modal-action">
          <button className="btn" onClick={onClose}>
            キャンセル
          </button>
          <button
            className="btn btn-error"
            onClick={() => {
              onConfirm();
              onClose();
            }}
          >
            削除する
          </button>
        </div>
      </div>
      <div className="modal-backdrop" onClick={onClose} />
    </dialog>
  );
}
