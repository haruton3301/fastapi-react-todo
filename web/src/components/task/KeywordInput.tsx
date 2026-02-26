import { useEffect, useRef, useState } from "react";

type Props = {
  value: string;
  onChange: (value: string) => void;
};

export function KeywordInput({ value, onChange }: Props) {
  const [buf, setBuf] = useState(value);
  const isComposing = useRef(false);

  useEffect(() => { setBuf(value); }, [value]);

  return (
    <div className="relative">
      <input
        type="text"
        placeholder="キーワードで検索..."
        className="input input-bordered w-full"
        value={buf}
        onChange={(e) => {
          setBuf(e.target.value);
          if (!isComposing.current) {
            onChange(e.target.value);
          }
        }}
        onCompositionStart={() => { isComposing.current = true; }}
        onCompositionEnd={(e) => {
          isComposing.current = false;
          onChange((e.target as HTMLInputElement).value);
        }}
      />
    </div>
  );
}
