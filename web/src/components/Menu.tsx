import React from "react";
import { NavLink } from "react-router-dom";
import "./Menu.css";

export default function Menu() {
  return (
    <nav className="main-menu">
      <NavLink
        to="/"
        className={({ isActive }) => (isActive ? "active" : undefined)}
        end
      >
        Dataset Preparation
      </NavLink>
      <NavLink
        to="/ml-predict"
        className={({ isActive }) => (isActive ? "active" : undefined)}
      >
        ML Prediction
      </NavLink>
    </nav>
  );
}
