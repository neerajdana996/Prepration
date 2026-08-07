import { useState } from "react";
import "./DualList.css";

// Starter data — replace with props if the interviewer asks for it.
const INITIAL_ITEMS = [
  { id: 1, label: "Apple" },
  { id: 2, label: "Banana" },
  { id: 3, label: "Cherry" },
  { id: 4, label: "Date" },
  { id: 5, label: "Elderberry" },
];

export default function DualList() {
  // Two lists of items.
  const [left, setLeft] = useState(INITIAL_ITEMS);
  const [right, setRight] = useState([]);

  // Which item ids are currently highlighted, per side.
  const [selectedLeft, setSelectedLeft] = useState(new Set());
  const [selectedRight, setSelectedRight] = useState(new Set());

  // --- Selection ---------------------------------------------------------
  // Toggle an item's highlight. Clicking a selected item deselects it.
  function toggleSelect(id, side) {
    // TODO: build a NEW Set (never mutate state directly),
    //       add id if absent, delete if present, then setSelected*.
  }

  // --- Moving items ------------------------------------------------------
  // Move the highlighted items from left -> right.
  function moveSelectedRight() {
    // TODO:
    //   1. moving = left.filter(item => selectedLeft.has(item.id))
    //   2. setRight([...right, ...moving])
    //   3. setLeft(left.filter(item => !selectedLeft.has(item.id)))
    //   4. clear selectedLeft
  }

  // Move the highlighted items from right -> left. Mirror of above.
  function moveSelectedLeft() {
    // TODO
  }

  // Move everything across, regardless of selection.
  function moveAllRight() {
    // TODO: setRight([...right, ...left]); setLeft([]); clear selection
  }

  function moveAllLeft() {
    // TODO
  }

  // --- Render ------------------------------------------------------------
  return (
    <div className="dual-list">
      <ListBox
        items={left}
        selected={selectedLeft}
        onItemClick={(id) => toggleSelect(id, "left")}
      />

      <div className="controls">
        <button onClick={moveAllRight}>&raquo;</button>
        <button onClick={moveSelectedRight}>&rsaquo;</button>
        <button onClick={moveSelectedLeft}>&lsaquo;</button>
        <button onClick={moveAllLeft}>&laquo;</button>
      </div>

      <ListBox
        items={right}
        selected={selectedRight}
        onItemClick={(id) => toggleSelect(id, "right")}
      />
    </div>
  );
}

// A single scrollable box of clickable rows.
function ListBox({ items, selected, onItemClick }) {
  return (
    <div className="list-box">
      {items.map((item) => (
        <div
          key={item.id}
          className={"list-item" + (selected.has(item.id) ? " selected" : "")}
          onClick={() => onItemClick(item.id)}
        >
          {item.label}
        </div>
      ))}
    </div>
  );
}
