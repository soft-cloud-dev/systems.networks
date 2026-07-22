#!/usr/bin/env python3
import sys
import re
import os
import shutil
import subprocess
import urllib.parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

PDF_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manuals_pdf")

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Systems Architecture · Learning Blueprint</title>
    <meta name="description" content="A layered map of infrastructure, runtime, trust, operations, control mechanics, knowledge, and governance.">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        /* ================================================================
           DESIGN TOKENS — Blueprint System
           ================================================================ */
        :root {
            --blue-900: #0A0E1A;
            --blue-800: #0D1533;
            --blue-700: #0044CC;
            --blue-600: #0066FF;
            --blue-500: #2E7DFF;
            --blue-400: #4DA3FF;
            --blue-300: #80BFFF;
            --blue-200: #B3D4FF;
            --blue-100: #D6EAFF;
            --blue-50:  #EBF4FF;
            --gray-900: #111827;
            --gray-700: #374151;
            --gray-600: #4B5563;
            --gray-500: #6B7280;
            --gray-400: #9CA3AF;
            --gray-300: #D1D5DB;
            --gray-200: #E5E7EB;
            --gray-100: #F3F4F6;
            --gray-50:  #F9FAFB;
            --white:    #FFFFFF;
            --red:      #EF4444;
            --green:    #10B981;

            --color-primary:    var(--blue-600);
            --color-bg:         var(--white);
            --color-surface:    var(--blue-900);
            --color-text:       var(--gray-900);
            --color-muted:      var(--gray-500);
            --color-border:     var(--gray-200);
            --color-border-mid: var(--gray-300);

            --font-sans: 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif;
            --font-mono: 'IBM Plex Mono', 'JetBrains Mono', 'SF Mono', Menlo, monospace;

            --radius: 0px;
            --grid-line: 1px solid var(--color-border);
            --spacing: 16px;
        }

        /* ================================================================
           RESET & BASE
           ================================================================ */
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        html { scroll-behavior: smooth; }
        body {
            font-family: var(--font-sans);
            background: var(--color-bg);
            color: var(--color-text);
            line-height: 1.5;
            font-size: 15px;
            -webkit-font-smoothing: antialiased;
        }

        /* ================================================================
           HEADER
           ================================================================ */
        .site-header {
            height: 56px;
            background: var(--white);
            border-bottom: var(--grid-line);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 40px;
            position: sticky;
            top: 0;
            z-index: 200;
        }
        .header-brand {
            font-family: var(--font-sans);
            font-weight: 600;
            font-size: 11px;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--blue-600);
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .brand-sep { color: var(--blue-300); letter-spacing: 0; }
        .header-nav { display: flex; align-items: center; gap: 8px; }
        .header-meta {
            font-family: var(--font-sans);
            font-size: 12px;
            color: var(--gray-500);
            margin-right: 28px;
        }
        .header-meta span { color: var(--gray-300); margin: 0 4px; }
        .header-nav a {
            font-family: var(--font-sans);
            font-weight: 500;
            font-size: 13px;
            color: var(--gray-600);
            text-decoration: none;
            padding: 4px 12px;
            transition: color 0.15s;
        }
        .header-nav a:hover { color: var(--blue-600); }
        .btn-primary {
            background: var(--blue-600);
            color: var(--white);
            border: none;
            padding: 8px 18px;
            font-family: var(--font-sans);
            font-weight: 600;
            font-size: 12px;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            cursor: pointer;
            transition: background 0.15s;
            margin-left: 8px;
        }
        .btn-primary:hover { background: var(--blue-700); }

        /* ================================================================
           HERO
           ================================================================ */
        .hero {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 72px 40px 64px;
            border-bottom: var(--grid-line);
            background: var(--white);
            position: relative;
            overflow: hidden;
            min-height: 380px;
        }
        .hero::before {
            content: '';
            position: absolute;
            inset: 0;
            background-image: radial-gradient(circle, #E5E7EB 1px, transparent 1px);
            background-size: 28px 28px;
            opacity: 0.5;
            pointer-events: none;
        }
        .hero-left { max-width: 580px; position: relative; z-index: 1; }
        .hero-eyebrow {
            font-family: var(--font-sans);
            font-weight: 600;
            font-size: 11px;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: var(--blue-600);
            margin-bottom: 28px;
        }
        .hero-title {
            font-family: var(--font-sans);
            font-weight: 700;
            font-size: clamp(42px, 5vw, 68px);
            line-height: 1.05;
            letter-spacing: -0.025em;
            color: var(--blue-900);
            margin-bottom: 28px;
        }
        .hero-subtitle {
            font-size: 16px;
            line-height: 1.65;
            color: var(--gray-500);
            max-width: 480px;
            margin-bottom: 36px;
        }
        .hero-label {
            font-family: var(--font-mono);
            font-weight: 700;
            font-size: 10px;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--gray-900);
        }
        .hero-right { position: relative; z-index: 1; flex-shrink: 0; margin-left: 48px; }
        .hero-diagram { width: 320px; height: 260px; }

        /* ================================================================
           SECTION LABELS
           ================================================================ */
        .section-label {
            font-family: var(--font-mono);
            font-weight: 500;
            font-size: 10px;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--gray-500);
            padding: 10px 40px;
            border-bottom: var(--grid-line);
            background: var(--gray-50);
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .section-label::before {
            content: '';
            width: 6px;
            height: 6px;
            background: var(--blue-600);
            flex-shrink: 0;
        }

        /* ================================================================
           TERMINAL DASHBOARD
           ================================================================ */
        .dashboard {
            display: flex;
            border-bottom: var(--grid-line);
            height: calc(100vh - 56px - 32px);
            min-height: 540px;
            position: relative;
        }
        .workspace-terminal {
            width: 60%;
            background: var(--blue-900);
            display: flex;
            flex-direction: column;
            border-right: 1px solid #1a2540;
        }
        .terminal-header {
            padding: 12px 24px;
            border-bottom: 1px solid #1a2540;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-shrink: 0;
            background: #080c18;
        }
        .terminal-header-title {
            font-family: var(--font-mono);
            font-size: 11px;
            font-weight: 500;
            color: var(--blue-400);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .terminal-header-title::before {
            content: '';
            width: 6px; height: 6px;
            background: var(--blue-500);
            border-radius: 50%;
            animation: status-blink 2s step-end infinite;
        }
        .terminal-header-status {
            display: flex;
            align-items: center;
            gap: 8px;
            font-family: var(--font-mono);
            font-size: 10px;
            color: #3A5080;
            letter-spacing: 0.08em;
        }
        .status-dot {
            width: 6px; height: 6px;
            background: var(--green);
            border-radius: 50%;
            animation: status-blink 2s step-end infinite;
        }
        @keyframes status-blink {
            0%, 80% { opacity: 1; }
            50%      { opacity: 0.3; }
        }
        .terminal-output {
            flex: 1;
            overflow-y: auto;
            padding: 20px 24px;
            font-family: var(--font-mono);
            font-size: 13px;
            color: #A8C4F0;
            line-height: 1.65;
        }
        .terminal-output::-webkit-scrollbar { width: 4px; }
        .terminal-output::-webkit-scrollbar-track { background: transparent; }
        .terminal-output::-webkit-scrollbar-thumb { background: #1e3060; border-radius: 2px; }
        .history-item { margin-bottom: 18px; }
        .cmd-line { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
        .cmd-prompt { color: var(--blue-500); font-weight: 700; }
        .cmd-text { color: #E2EEFF; font-weight: 500; }
        .cmd-output {
            white-space: pre-wrap;
            word-break: break-all;
            color: #5A7AB0;
            padding-left: 16px;
            border-left: 2px solid #1a2e50;
            margin-top: 4px;
        }
        .cmd-output.error { color: var(--red); border-left-color: var(--red); }
        .man-opened-notice {
            background: rgba(0,102,255,0.08);
            border: 1px solid rgba(0,102,255,0.25);
            padding: 10px 16px;
            margin-top: 6px;
            color: #A8C4F0;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 13px;
        }
        .man-opened-notice strong { color: var(--blue-400); font-family: var(--font-mono); }
        .btn-notice {
            background: var(--blue-600);
            color: var(--white);
            border: none;
            padding: 4px 12px;
            font-weight: 700;
            font-size: 10px;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            cursor: pointer;
            transition: background 0.15s;
        }
        .btn-notice:hover { background: var(--blue-700); }
        .welcome-art { color: #1e3060; margin-bottom: 16px; line-height: 1.3; font-size: 11px; }
        .welcome-art .highlight { color: var(--blue-500); }
        .terminal-input-bar {
            display: flex;
            align-items: center;
            padding: 12px 24px;
            border-top: 1px solid #1a2540;
            gap: 10px;
            flex-shrink: 0;
            background: #060a14;
        }
        .input-prompt { color: var(--blue-500); font-family: var(--font-mono); font-weight: 700; font-size: 13px; flex-shrink: 0; }
        .terminal-input-bar input {
            flex: 1; background: none; border: none; outline: none;
            color: #E2EEFF; font-family: var(--font-mono); font-size: 13px; caret-color: var(--blue-400);
        }
        .terminal-input-bar input::placeholder { color: #2a3f6a; }
        .terminal-input-bar button {
            background: transparent; color: var(--blue-400); border: 1px solid #1e3560;
            padding: 5px 14px; font-family: var(--font-mono); font-weight: 700; font-size: 10px;
            letter-spacing: 0.08em; text-transform: uppercase; cursor: pointer; transition: all 0.15s;
        }
        .terminal-input-bar button:hover { background: var(--blue-600); border-color: var(--blue-600); color: var(--white); }

        /* Connector Bridge */
        .connector-bridge {
            width: 40px; background: var(--white); border-right: var(--grid-line);
            position: relative; flex-shrink: 0; display: flex; align-items: center;
            justify-content: center; overflow: hidden;
        }
        .connector-svg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }
        .connector-path { stroke: var(--blue-600); stroke-width: 2; fill: none; opacity: 0.2; transition: opacity 0.4s; }
        .connector-path.active { opacity: 1; animation: connector-flash 0.5s ease; }
        .connector-dot { fill: var(--blue-600); opacity: 0.2; transition: opacity 0.4s; }
        .connector-dot.active { opacity: 1; }
        @keyframes connector-flash { 0% { opacity: 0.2; } 40% { opacity: 1; } 100% { opacity: 1; } }

        /* Manual Panel */
        .workspace-manual { width: calc(40% - 40px); background: var(--white); display: flex; flex-direction: column; overflow: hidden; }
        .manual-header {
            padding: 14px 24px; border-bottom: var(--grid-line);
            display: flex; align-items: center; justify-content: space-between;
            flex-shrink: 0; background: var(--gray-50);
        }
        .manual-header-left { display: flex; align-items: center; gap: 10px; }
        .manual-badge {
            font-family: var(--font-mono); font-size: 10px; font-weight: 700;
            color: var(--blue-600); border: 1px solid var(--blue-200); background: var(--blue-50);
            padding: 2px 8px; letter-spacing: 0.06em; text-transform: uppercase;
        }
        .manual-title { font-family: var(--font-sans); font-weight: 600; font-size: 14px; color: var(--gray-900); }
        .manual-toolbar {
            padding: 8px 24px; border-bottom: var(--grid-line);
            display: flex; align-items: center; justify-content: space-between;
            flex-shrink: 0; background: var(--white);
        }
        .view-toggle { display: flex; border: var(--grid-line); }
        .view-btn {
            background: none; border: none; border-right: var(--grid-line);
            padding: 5px 14px; font-family: var(--font-mono); font-size: 10px;
            font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase;
            color: var(--gray-500); cursor: pointer; transition: all 0.15s;
        }
        .view-btn:last-child { border-right: none; }
        .view-btn.active { background: var(--blue-600); color: var(--white); }
        .view-btn:hover:not(.active) { background: var(--blue-50); color: var(--blue-600); }
        .back-btn {
            background: none; border: var(--grid-line); padding: 5px 14px;
            font-family: var(--font-mono); font-size: 10px; font-weight: 600;
            letter-spacing: 0.06em; text-transform: uppercase; color: var(--gray-600);
            cursor: pointer; transition: all 0.15s;
        }
        .back-btn:hover { background: var(--blue-50); color: var(--blue-600); border-color: var(--blue-200); }
        .manual-search { padding: 10px 24px; border-bottom: var(--grid-line); flex-shrink: 0; }
        .manual-search input {
            width: 100%; background: var(--white); border: var(--grid-line);
            color: var(--gray-900); padding: 7px 12px; font-family: var(--font-mono);
            font-size: 12px; outline: none; transition: border-color 0.2s;
        }
        .manual-search input:focus { border-color: var(--blue-600); }
        .manual-search input::placeholder { color: var(--gray-400); }
        .manual-body { flex: 1; overflow-y: auto; padding: 0; }
        .manual-body::-webkit-scrollbar { width: 4px; }
        .manual-body::-webkit-scrollbar-track { background: transparent; }
        .manual-body::-webkit-scrollbar-thumb { background: var(--gray-300); }
        .manual-list { list-style: none; }
        .manual-item {
            padding: 11px 24px; cursor: pointer; border-bottom: 1px solid var(--gray-100);
            border-left: 3px solid transparent; transition: all 0.1s;
            display: flex; flex-direction: column; gap: 3px;
        }
        .manual-item:hover { background: var(--blue-50); border-left-color: var(--blue-600); }
        .manual-item.active { background: var(--white); border-left-color: var(--blue-600); }
        .man-head { display: flex; align-items: center; justify-content: space-between; }
        .man-name { font-family: var(--font-mono); font-size: 13px; font-weight: 700; color: var(--gray-900); }
        .man-sec {
            font-family: var(--font-mono); font-size: 9px; font-weight: 600;
            color: var(--blue-600); background: var(--blue-50); border: 1px solid var(--blue-100);
            padding: 1px 6px; letter-spacing: 0.05em; text-transform: uppercase;
        }
        .man-desc { font-size: 11px; color: var(--gray-500); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .manual-count { font-family: var(--font-mono); font-size: 10px; color: var(--gray-400); letter-spacing: 0.04em; }
        .manual-content { height: 100%; display: flex; flex-direction: column; }
        .manual-content iframe { width: 100%; flex: 1; border: none; background: var(--white); }
        .raw-view {
            background: var(--blue-900); padding: 20px 24px; font-family: var(--font-mono);
            font-size: 12px; color: #A8C4F0; white-space: pre-wrap; word-break: break-all;
            line-height: 1.65; height: 100%; overflow-y: auto;
        }
        .loading-state {
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            padding: 48px 24px; gap: 14px; color: var(--gray-400);
            font-family: var(--font-mono); font-size: 11px; letter-spacing: 0.06em;
        }
        .loading-block { width: 12px; height: 12px; background: var(--blue-600); animation: block-blink 500ms step-end infinite; }
        @keyframes block-blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }

        /* Quick Actions */
        .quick-actions {
            padding: 8px 24px; background: #080c18; border-bottom: 1px solid #1a2540;
            display: flex; align-items: center; gap: 6px; flex-wrap: wrap; flex-shrink: 0;
        }
        .quick-label { font-family: var(--font-mono); font-size: 9px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: #2a4070; margin-right: 4px; }
        .chip { background: none; border: 1px solid #1a3060; color: #3A5A90; padding: 3px 10px; font-family: var(--font-mono); font-size: 11px; cursor: pointer; transition: all 0.12s; }
        .chip:hover { border-color: var(--blue-500); color: var(--blue-300); }
        .chip-man { border-color: rgba(0,102,255,0.3); color: var(--blue-400); }
        .chip-man:hover { background: rgba(0,102,255,0.1); border-color: var(--blue-500); color: var(--blue-300); }

        /* ================================================================
           LAYER MAP
           ================================================================ */
        .layer-map-section {
            border-bottom: var(--grid-line);
            display: grid;
            grid-template-columns: 1fr 1fr;
        }
        .layer-map-left { padding: 48px 40px; border-right: var(--grid-line); }
        .layer-map-title {
            font-family: var(--font-sans); font-weight: 700; font-size: 28px;
            color: var(--blue-900); letter-spacing: -0.02em; margin-bottom: 16px;
        }
        .layer-map-desc { font-size: 14px; color: var(--gray-500); line-height: 1.65; margin-bottom: 32px; }
        .layer-list { list-style: none; display: flex; flex-direction: column; }
        .layer-item { display: flex; align-items: center; gap: 14px; padding: 12px 0; border-bottom: 1px solid var(--gray-100); }
        .layer-num { font-family: var(--font-mono); font-size: 10px; font-weight: 700; color: var(--blue-400); letter-spacing: 0.08em; width: 32px; flex-shrink: 0; }
        .layer-name { font-family: var(--font-sans); font-weight: 600; font-size: 13px; color: var(--blue-900); flex: 1; }
        .layer-desc { font-size: 12px; color: var(--gray-400); }
        .layer-dot { width: 8px; height: 8px; background: var(--blue-200); flex-shrink: 0; }
        .layer-map-right {
            padding: 48px 40px; display: flex; align-items: center; justify-content: center;
            background-image: radial-gradient(circle, #E5E7EB 1px, transparent 1px);
            background-size: 28px 28px;
        }
        .layer-diagram-large { width: 380px; height: 300px; }

        /* ================================================================
           SYSTEM ARCHITECTURE
           ================================================================ */
        .architecture { border-bottom: var(--grid-line); }
        .architecture-grid {
            display: grid; grid-template-columns: 1fr 1fr 1fr;
            background-image: radial-gradient(circle, #D1D5DB 1px, transparent 1px);
            background-size: 24px 24px; position: relative;
        }
        .module-card { padding: 36px 32px; border-right: var(--grid-line); background: transparent; transition: background 0.2s; position: relative; }
        .module-card:last-child { border-right: none; }
        .module-card::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 3px; background: transparent; transition: background 0.2s; }
        .module-card:hover { background: rgba(255,255,255,0.92); }
        .module-card:hover::before { background: var(--blue-600); }
        .module-card:hover .module-flow-dot { background: var(--blue-600); }
        .module-number { font-family: var(--font-mono); font-size: 10px; font-weight: 700; color: var(--blue-400); letter-spacing: 0.12em; margin-bottom: 14px; }
        .module-title { font-family: var(--font-sans); font-weight: 700; font-size: 20px; color: var(--blue-900); letter-spacing: -0.02em; margin-bottom: 10px; }
        .module-desc { font-size: 13px; color: var(--gray-500); line-height: 1.55; margin-bottom: 20px; }
        .module-meta { display: flex; align-items: center; gap: 12px; }
        .module-tag { font-family: var(--font-mono); font-size: 10px; font-weight: 600; color: var(--blue-700); background: var(--blue-50); border: 1px solid var(--blue-100); padding: 3px 10px; text-transform: uppercase; letter-spacing: 0.06em; }
        .module-flow-dot { width: 8px; height: 8px; background: var(--gray-300); transition: background 0.2s; }
        .architecture-flow { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 1; }
        .flow-line { stroke: var(--gray-300); stroke-width: 1.5; fill: none; stroke-dasharray: 6 4; transition: stroke 0.2s; }
        .flow-arrow { fill: var(--gray-300); transition: fill 0.2s; }

        /* ================================================================
           API SCHEMATICS
           ================================================================ */
        .api-schematics { border-bottom: var(--grid-line); }
        .api-map {
            padding: 36px 40px; border-bottom: var(--grid-line);
            display: flex; align-items: center; justify-content: center;
            background-image: radial-gradient(circle, #D1D5DB 1px, transparent 1px);
            background-size: 24px 24px;
        }
        .api-node { padding: 14px 24px; border: 1.5px solid var(--blue-900); background: var(--white); font-family: var(--font-mono); font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; transition: all 0.2s; color: var(--blue-900); }
        .api-node.highlight { border-color: var(--blue-600); color: var(--blue-600); background: var(--blue-50); }
        .api-node-arrow { width: 40px; height: 2px; background: var(--blue-900); position: relative; flex-shrink: 0; }
        .api-node-arrow::after { content: ''; position: absolute; right: -1px; top: -4px; width: 0; height: 0; border-left: 7px solid var(--blue-900); border-top: 4px solid transparent; border-bottom: 4px solid transparent; }
        .api-endpoints { display: grid; grid-template-columns: 1fr 1fr; }
        .api-endpoint { padding: 24px 32px; border-right: var(--grid-line); border-bottom: var(--grid-line); cursor: pointer; border-left: 3px solid transparent; transition: all 0.12s; }
        .api-endpoint:nth-child(even) { border-right: none; }
        .api-endpoint:hover, .api-endpoint.active { border-left-color: var(--blue-600); background: var(--blue-50); }
        .endpoint-header { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
        .method-badge { font-family: var(--font-mono); font-size: 10px; font-weight: 700; color: var(--blue-600); background: var(--blue-50); border: 1px solid var(--blue-200); padding: 2px 8px; letter-spacing: 0.05em; }
        .method-badge.post { color: var(--blue-900); background: var(--gray-100); border-color: var(--gray-300); }
        .endpoint-path { font-family: var(--font-mono); font-size: 13px; font-weight: 500; color: var(--gray-900); }
        .endpoint-desc { font-size: 13px; color: var(--gray-500); margin-bottom: 10px; }
        .endpoint-params { font-family: var(--font-mono); font-size: 11px; color: var(--gray-400); }
        .endpoint-params .param-key { color: var(--gray-700); font-weight: 600; }
        .param-callout { color: var(--blue-600); font-weight: 700; }

        /* ================================================================
           ENGINEERING LOGS
           ================================================================ */
        .engineering-logs { display: grid; grid-template-columns: 180px 220px 1fr auto; border-top: var(--grid-line); background: var(--white); }
        .log-cell { padding: 16px 24px; border-right: var(--grid-line); display: flex; flex-direction: column; gap: 6px; }
        .log-cell:last-child { border-right: none; }
        .log-label { font-family: var(--font-sans); font-weight: 600; font-size: 9px; letter-spacing: 0.12em; text-transform: uppercase; color: var(--gray-400); }
        .log-value { font-family: var(--font-mono); font-size: 12px; font-weight: 500; color: var(--gray-700); display: flex; align-items: center; gap: 8px; }
        .status-indicator { width: 7px; height: 7px; flex-shrink: 0; }
        .status-indicator.ok { background: var(--green); animation: status-blink 2s step-end infinite; border-radius: 50%; }
        .status-indicator.err { background: var(--red); animation: status-blink 1s step-end infinite; border-radius: 50%; }
        .log-mini-terminal { font-family: var(--font-mono); font-size: 10px; color: var(--gray-400); line-height: 1.6; max-height: 56px; overflow: hidden; }
        .log-mini-terminal .log-entry { white-space: nowrap; }
        .log-mini-terminal .log-ts { color: var(--gray-300); }
        .stamp { width: 52px; height: 52px; border: 1.5px solid var(--blue-600); border-radius: 50%; display: flex; align-items: center; justify-content: center; transform: rotate(15deg); font-family: var(--font-mono); font-weight: 700; font-size: 9px; letter-spacing: 0.12em; color: var(--blue-600); flex-shrink: 0; position: relative; }
        .stamp::before { content: ''; position: absolute; inset: 3px; border: 1px solid var(--blue-200); border-radius: 50%; }

        /* UTILITIES */
        code { font-family: var(--font-mono); font-size: 0.9em; color: var(--blue-600); }
        @keyframes cursor-blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
        .cursor-block { display: inline-block; width: 7px; height: 13px; background: var(--blue-500); animation: cursor-blink 500ms step-end infinite; vertical-align: text-bottom; }
    </style>
</head>
<body>

    <!-- HEADER -->
    <header class="site-header">
        <div class="header-brand">
            SYSTEMS ARCHITECTURE <span class="brand-sep">&middot;</span> LEARNING BLUEPRINT
        </div>
        <nav class="header-nav">
            <span class="header-meta">7 layers <span>&middot;</span> 23 domains <span>&middot;</span> one control model</span>
            <a href="#architecture">Architecture</a>
            <a href="#manual-panel">Manual</a>
            <a href="#api">API</a>
            <button class="btn-primary" onclick="document.getElementById('cmdInput').focus()">Get Started</button>
        </nav>
    </header>

    <!-- HERO -->
    <section class="hero">
        <div class="hero-left">
            <div class="hero-eyebrow">Systems Architecture &middot; Learning Blueprint</div>
            <h1 class="hero-title">From metal<br>to meaning</h1>
            <p class="hero-subtitle">A layered map of infrastructure, runtime, trust, operations, control mechanics, knowledge, and governance.</p>
            <div class="hero-label">TECHNICAL CAPABILITY MAP</div>
        </div>
        <div class="hero-right">
            <svg class="hero-diagram" viewBox="0 0 320 260" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="0" y="0" width="320" height="260" fill="#CCE4FF"/>
                <rect x="60" y="36" width="260" height="188" fill="#4DA3FF"/>
                <rect x="128" y="80" width="192" height="144" fill="#0066FF"/>
            </svg>
        </div>
    </section>

    <!-- TERMINAL DASHBOARD -->
    <div class="section-label">Terminal Dashboard &mdash; Live CLI Workspace</div>
    <section class="dashboard" id="dashboard">
        <div class="workspace-terminal">
            <div class="terminal-header">
                <span class="terminal-header-title">Terminal &mdash; /bin/sh</span>
                <span class="terminal-header-status"><span class="status-dot"></span> CONNECTED</span>
            </div>
            <div class="quick-actions">
                <span class="quick-label">Quick:</span>
                <button class="chip chip-man" onclick="executeManCommand('man ls')">man ls</button>
                <button class="chip chip-man" onclick="executeManCommand('man grep')">man grep</button>
                <button class="chip chip-man" onclick="executeManCommand('man curl')">man curl</button>
                <button class="chip chip-man" onclick="executeManCommand('man find')">man find</button>
                <button class="chip" onclick="runCommand('whoami')">whoami</button>
                <button class="chip" onclick="runCommand('uname -a')">uname -a</button>
                <button class="chip" onclick="runCommand('df -h')">df -h</button>
            </div>
            <div class="terminal-output" id="terminal">
                <div class="welcome-art"><span class="highlight">&#9484;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9488;</span>
<span class="highlight">&#9474;</span>  S C H E M A T I C   F L U X   v2.4.11 <span class="highlight">&#9474;</span>
<span class="highlight">&#9474;</span>  Systems Architecture Blueprint Shell   <span class="highlight">&#9474;</span>
<span class="highlight">&#9492;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9496;</span></div>
                <div class="history-item">
                    <div class="cmd-line"><span class="cmd-prompt">user@flux ~ $</span> <span class="cmd-text">echo "Ready"</span></div>
                    <div class="cmd-output">Execute commands or type <code>man {command}</code> to load documentation in the manual panel. <span class="cursor-block"></span></div>
                </div>
            </div>
            <form class="terminal-input-bar" onsubmit="handleFormSubmit(event)">
                <span class="input-prompt">user@flux ~ $</span>
                <input type="text" id="cmdInput" placeholder="Enter command or man &lt;cmd&gt;..." autofocus autocomplete="off">
                <button type="submit">Execute</button>
            </form>
        </div>

        <div class="connector-bridge">
            <svg class="connector-svg" id="connectorSvg" viewBox="0 0 40 600" preserveAspectRatio="none">
                <path class="connector-path" id="connectorPath" d="M 0 320 H 20 V 80 H 40" />
                <circle class="connector-dot" id="connectorDotL" cx="0" cy="320" r="4" />
                <circle class="connector-dot" id="connectorDotR" cx="40" cy="80" r="4" />
            </svg>
        </div>

        <div class="workspace-manual" id="manual-panel">
            <div class="manual-header">
                <div class="manual-header-left">
                    <span class="manual-badge" id="manBadge">MAN(1)</span>
                    <span class="manual-title" id="manTitle">Manual Pages</span>
                </div>
                <span class="manual-count" id="manCount">30 entries</span>
            </div>
            <div class="manual-toolbar" id="manToolbar" style="display:none;">
                <button class="back-btn" onclick="showManList()">&larr; INDEX</button>
                <div class="view-toggle">
                    <button class="view-btn active" id="btnViewPdf" onclick="setManViewMode('pdf')">PDF</button>
                    <button class="view-btn" id="btnViewRaw" onclick="setManViewMode('raw')">RAW</button>
                </div>
            </div>
            <div class="manual-search" id="manSearchWrap">
                <input type="text" id="manualSearch" placeholder="Filter manuals..." oninput="filterManuals(this.value)">
            </div>
            <div class="manual-body" id="manBody">
                <ul class="manual-list" id="manualList"></ul>
            </div>
        </div>
    </section>

    <!-- LAYER MAP -->
    <div class="section-label" id="layer-map-label">Layer Map &mdash; System Topology</div>
    <section class="layer-map-section">
        <div class="layer-map-left">
            <div class="layer-map-title">Seven layers,<br>one control model</div>
            <p class="layer-map-desc">Each layer encapsulates a distinct domain of concern &mdash; from bare metal to governance &mdash; connected by a unified operational model.</p>
            <ul class="layer-list">
                <li class="layer-item"><span class="layer-num">L01</span><span class="layer-dot"></span><span class="layer-name">Infrastructure</span><span class="layer-desc">Compute, network, storage</span></li>
                <li class="layer-item"><span class="layer-num">L02</span><span class="layer-dot"></span><span class="layer-name">Runtime</span><span class="layer-desc">Containers, runtimes, VMs</span></li>
                <li class="layer-item"><span class="layer-num">L03</span><span class="layer-dot"></span><span class="layer-name">Trust</span><span class="layer-desc">Identity, auth, certificates</span></li>
                <li class="layer-item"><span class="layer-num">L04</span><span class="layer-dot"></span><span class="layer-name">Operations</span><span class="layer-desc">Scheduling, orchestration</span></li>
                <li class="layer-item"><span class="layer-num">L05</span><span class="layer-dot"></span><span class="layer-name">Control Mechanics</span><span class="layer-desc">API surfaces, state machines</span></li>
                <li class="layer-item"><span class="layer-num">L06</span><span class="layer-dot"></span><span class="layer-name">Knowledge</span><span class="layer-desc">Observability, documentation</span></li>
                <li class="layer-item"><span class="layer-num">L07</span><span class="layer-dot"></span><span class="layer-name">Governance</span><span class="layer-desc">Policy, compliance, audit</span></li>
            </ul>
        </div>
        <div class="layer-map-right">
            <svg class="layer-diagram-large" viewBox="0 0 380 300" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="0" y="0" width="380" height="300" fill="#EBF4FF"/>
                <text x="8" y="14" font-family="'IBM Plex Mono', monospace" font-size="9" font-weight="700" fill="#4DA3FF" letter-spacing="0.1em">L07 GOVERNANCE</text>
                <rect x="28" y="30" width="324" height="242" fill="#CCE4FF"/>
                <text x="36" y="44" font-family="'IBM Plex Mono', monospace" font-size="9" font-weight="700" fill="#0066FF" letter-spacing="0.08em">L06 KNOWLEDGE</text>
                <rect x="56" y="58" width="268" height="186" fill="#80BFFF"/>
                <text x="64" y="72" font-family="'IBM Plex Mono', monospace" font-size="9" font-weight="700" fill="#0044CC" letter-spacing="0.08em">L05 CONTROL</text>
                <rect x="84" y="86" width="212" height="130" fill="#4DA3FF"/>
                <text x="92" y="100" font-family="'IBM Plex Mono', monospace" font-size="9" font-weight="700" fill="#FFFFFF" letter-spacing="0.08em">L04 OPERATIONS</text>
                <rect x="112" y="112" width="156" height="76" fill="#2E7DFF"/>
                <text x="120" y="126" font-family="'IBM Plex Mono', monospace" font-size="9" font-weight="700" fill="#FFFFFF" letter-spacing="0.08em">L03 TRUST</text>
                <rect x="140" y="138" width="100" height="36" fill="#0066FF"/>
                <text x="148" y="161" font-family="'IBM Plex Mono', monospace" font-size="8" font-weight="700" fill="#FFFFFF" letter-spacing="0.06em">L02 RUNTIME</text>
                <rect x="164" y="176" width="52" height="18" fill="#0044CC"/>
                <text x="171" y="189" font-family="'IBM Plex Mono', monospace" font-size="7" font-weight="700" fill="#FFFFFF" letter-spacing="0.04em">L01 INFRA</text>
            </svg>
        </div>
    </section>

    <!-- SYSTEM ARCHITECTURE -->
    <div class="section-label" id="architecture">System Architecture &mdash; Module Overview</div>
    <section class="architecture">
        <div class="architecture-grid" id="archGrid">
            <svg class="architecture-flow" id="archFlow" viewBox="0 0 1200 180" preserveAspectRatio="none">
                <line class="flow-line" x1="400" y1="90" x2="400" y2="90" />
                <line class="flow-line" x1="800" y1="90" x2="800" y2="90" />
            </svg>
            <div class="module-card" data-module="pdf">
                <div class="module-number">MODULE 01</div>
                <div class="module-title">PDF Viewer</div>
                <div class="module-desc">Renders LaTeX-compiled manual pages as high-fidelity PDF documents within the terminal interface.</div>
                <div class="module-meta"><span class="module-tag">Renderer</span><span class="module-flow-dot"></span></div>
            </div>
            <div class="module-card" data-module="latex">
                <div class="module-number">MODULE 02</div>
                <div class="module-title">LaTeX Generator</div>
                <div class="module-desc">Compiles raw man page text into structured LaTeX documents with branded typography and layout.</div>
                <div class="module-meta"><span class="module-tag">Compiler</span><span class="module-flow-dot"></span></div>
            </div>
            <div class="module-card" data-module="api">
                <div class="module-number">MODULE 03</div>
                <div class="module-title">API Interop</div>
                <div class="module-desc">RESTful HTTP endpoints for command execution, manual retrieval, and PDF generation.</div>
                <div class="module-meta"><span class="module-tag">Interface</span><span class="module-flow-dot"></span></div>
            </div>
        </div>
    </section>

    <!-- API SCHEMATICS -->
    <div class="section-label" id="api">API Schematics &mdash; Endpoint Specifications</div>
    <section class="api-schematics">
        <div class="api-map">
            <div class="api-node" id="nodeClient">CLIENT</div>
            <div class="api-node-arrow"></div>
            <div class="api-node" id="nodeGateway">GATEWAY</div>
            <div class="api-node-arrow"></div>
            <div class="api-node" id="nodeShell">SHELL EXEC</div>
            <div class="api-node-arrow"></div>
            <div class="api-node" id="nodePdf">PDF ENGINE</div>
        </div>
        <div class="api-endpoints">
            <div class="api-endpoint active" onclick="highlightNode('nodeShell')">
                <div class="endpoint-header"><span class="method-badge">GET</span><span class="endpoint-path">/v1/{command}</span></div>
                <div class="endpoint-desc">Execute a shell command and return plain-text output.</div>
                <div class="endpoint-params"><span class="param-key">command</span> : string &mdash; <span class="param-callout">[</span>required<span class="param-callout">]</span> Shell command to execute</div>
            </div>
            <div class="api-endpoint" onclick="highlightNode('nodePdf')">
                <div class="endpoint-header"><span class="method-badge">GET</span><span class="endpoint-path">/pdf/{command}</span></div>
                <div class="endpoint-desc">Generate and return a LaTeX-compiled PDF manual page.</div>
                <div class="endpoint-params"><span class="param-key">command</span> : string &mdash; <span class="param-callout">[</span>required<span class="param-callout">]</span> Man page target</div>
            </div>
            <div class="api-endpoint" onclick="highlightNode('nodeShell')">
                <div class="endpoint-header"><span class="method-badge post">POST</span><span class="endpoint-path">/</span></div>
                <div class="endpoint-desc">Execute a command provided in the POST request body.</div>
                <div class="endpoint-params"><span class="param-key">body</span> : text &mdash; <span class="param-callout">[</span>required<span class="param-callout">]</span> Raw command string</div>
            </div>
            <div class="api-endpoint" onclick="highlightNode('nodeGateway')">
                <div class="endpoint-header"><span class="method-badge">GET</span><span class="endpoint-path">/man/{command}</span></div>
                <div class="endpoint-desc">Retrieve raw manual page text for a given command.</div>
                <div class="endpoint-params"><span class="param-key">command</span> : string &mdash; <span class="param-callout">[</span>required<span class="param-callout">]</span> Manual target</div>
            </div>
        </div>
    </section>

    <!-- ENGINEERING LOGS -->
    <footer class="engineering-logs">
        <div class="log-cell">
            <span class="log-label">Security Status</span>
            <span class="log-value"><span class="status-indicator ok" id="secStatus"></span><span id="secText">OPERATIONAL</span></span>
        </div>
        <div class="log-cell">
            <span class="log-label">License &amp; Build</span>
            <span class="log-value">MIT License / v2.4.11</span>
        </div>
        <div class="log-cell" id="logCell">
            <span class="log-label">System Logs</span>
            <div class="log-mini-terminal" id="sysLogs"></div>
        </div>
        <div class="log-cell" style="align-items:center;justify-content:center;">
            <div class="stamp">APVD</div>
        </div>
    </footer>

    <script>
        const terminal = document.getElementById('terminal');
        const cmdInput = document.getElementById('cmdInput');
        let currentRawMan = '', currentCmdName = '', currentViewMode = 'pdf', panelState = 'list';

        const manuals = [
            { name: 'intro', sec: '1', desc: 'Introduction to user commands' },
            { name: 'man',   sec: '1', desc: 'Format and display manual pages' },
            { name: 'bash',  sec: '1', desc: 'GNU Bourne-Again SHell' },
            { name: 'ash',   sec: '1', desc: 'Almquist shell command interpreter' },
            { name: 'sh',    sec: '1', desc: 'Command usage & Unix shell interpreter' },
            { name: 'ls',    sec: '1', desc: 'List directory contents' },
            { name: 'cat',   sec: '1', desc: 'Concatenate files and print on stdout' },
            { name: 'cp',    sec: '1', desc: 'Copy files and directories' },
            { name: 'mv',    sec: '1', desc: 'Move (rename) files' },
            { name: 'rm',    sec: '1', desc: 'Remove files or directories' },
            { name: 'mkdir', sec: '1', desc: 'Make directories' },
            { name: 'rmdir', sec: '1', desc: 'Remove empty directories' },
            { name: 'chmod', sec: '1', desc: 'Change file mode bits' },
            { name: 'chown', sec: '1', desc: 'Change file owner and group' },
            { name: 'grep',  sec: '1', desc: 'Print lines matching a pattern' },
            { name: 'find',  sec: '1', desc: 'Search for files in a directory hierarchy' },
            { name: 'ps',    sec: '1', desc: 'Report a snapshot of current processes' },
            { name: 'kill',  sec: '1', desc: 'Send a signal to a process' },
            { name: 'df',    sec: '1', desc: 'Report file system disk space usage' },
            { name: 'mount', sec: '8', desc: 'Mount a filesystem' },
            { name: 'umount',sec: '8', desc: 'Unmount a filesystem' },
            { name: 'tar',   sec: '1', desc: 'Archiving utility' },
            { name: 'curl',  sec: '1', desc: 'Transfer data from or to a server' },
            { name: 'date',  sec: '1', desc: 'Display or set system date and time' },
            { name: 'uptime',sec: '1', desc: 'Tell how long system has been running' },
            { name: 'whoami',sec: '1', desc: 'Print effective user name' },
            { name: 'head',  sec: '1', desc: 'Output the first part of files' },
            { name: 'tail',  sec: '1', desc: 'Output the last part of files' },
            { name: 'sed',   sec: '1', desc: 'Stream editor for filtering and transforming text' },
            { name: 'awk',   sec: '1', desc: 'Pattern scanning and processing language' }
        ];

        function cleanCmdName(cmd) {
            if (!cmd) return 'intro';
            let c = String(cmd).trim();
            if (c.toLowerCase().startsWith('man ')) c = c.substring(4).trim();
            return c.replace(/[^a-zA-Z0-9_\-]/g, '') || 'intro';
        }
        function escapeHtml(str) {
            return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#039;');
        }

        function renderManuals(filter = '') {
            const list = document.getElementById('manualList');
            list.innerHTML = '';
            const query = filter.toLowerCase().trim();
            const filtered = manuals.filter(m => m.name.toLowerCase().includes(query) || m.desc.toLowerCase().includes(query));
            document.getElementById('manCount').textContent = filtered.length + ' entries';
            filtered.forEach(m => {
                const li = document.createElement('li');
                li.className = 'manual-item';
                if (currentCmdName === m.name) li.classList.add('active');
                li.onclick = () => {
                    document.querySelectorAll('.manual-item').forEach(el => el.classList.remove('active'));
                    li.classList.add('active');
                    openManContent(m.name);
                };
                li.innerHTML = `<div class="man-head"><span class="man-name">${m.name}</span><span class="man-sec">man(${m.sec})</span></div><div class="man-desc">${m.desc}</div>`;
                list.appendChild(li);
            });
        }
        function filterManuals(val) { renderManuals(val); }

        function showManList() {
            panelState = 'list'; currentCmdName = '';
            document.getElementById('manToolbar').style.display = 'none';
            document.getElementById('manSearchWrap').style.display = 'block';
            document.getElementById('manBadge').textContent = 'MAN(1)';
            document.getElementById('manTitle').textContent = 'Manual Pages';
            const body = document.getElementById('manBody');
            body.innerHTML = '<ul class="manual-list" id="manualList"></ul>';
            renderManuals(document.getElementById('manualSearch').value);
            setConnectorActive(false);
        }

        async function openManContent(cmdName) {
            const cleanName = cleanCmdName(cmdName);
            currentCmdName = cleanName; panelState = 'content';
            document.getElementById('manToolbar').style.display = 'flex';
            document.getElementById('manSearchWrap').style.display = 'none';
            document.getElementById('manBadge').textContent = 'MAN(1)';
            document.getElementById('manTitle').textContent = cleanName;
            setConnectorActive(true);
            const body = document.getElementById('manBody');
            body.innerHTML = `<div class="loading-state"><div class="loading-block"></div><span>Loading documentation for '${cleanName}'...</span></div>`;
            try {
                const res = await fetch('/' + encodeURIComponent('man ' + cleanName));
                const text = await res.text();
                currentRawMan = text;
                renderCurrentView();
            } catch (err) {
                body.innerHTML = '<div style="padding:24px;color:var(--red);font-family:var(--font-mono);font-size:13px;">[ERR_CODE_X9] Failed to load manual: ' + escapeHtml(err.message) + '</div>';
            }
        }

        function setManViewMode(mode) {
            currentViewMode = mode;
            document.getElementById('btnViewPdf').classList.toggle('active', mode === 'pdf');
            document.getElementById('btnViewRaw').classList.toggle('active', mode === 'raw');
            renderCurrentView();
        }

        function renderCurrentView() {
            const body = document.getElementById('manBody');
            if (currentViewMode === 'raw') {
                body.innerHTML = '<div class="raw-view">' + escapeHtml(currentRawMan) + '</div>';
                return;
            }
            const cleanName = cleanCmdName(currentCmdName);
            body.innerHTML = '<div class="manual-content"><iframe src="/pdf/' + cleanName + '" title="' + cleanName + ' manual PDF"></iframe></div>';
        }

        function setConnectorActive(active) {
            const path = document.getElementById('connectorPath');
            const dotL = document.getElementById('connectorDotL');
            const dotR = document.getElementById('connectorDotR');
            path.classList.toggle('active', active);
            dotL.classList.toggle('active', active);
            dotR.classList.toggle('active', active);
        }

        async function runCommand(cmd) {
            if (!cmd.trim()) return;
            const trimmed = cmd.trim();
            if (trimmed.startsWith('man ') || trimmed === 'man') {
                const parts = trimmed.split(/\s+/);
                executeManCommand('man ' + (parts[1] || 'man'));
                return;
            }
            const item = document.createElement('div');
            item.className = 'history-item';
            item.innerHTML = '<div class="cmd-line"><span class="cmd-prompt">user@flux ~ $</span> <span class="cmd-text"></span></div><div class="cmd-output">Running...</div>';
            item.querySelector('.cmd-text').textContent = cmd;
            terminal.appendChild(item);
            terminal.scrollTop = terminal.scrollHeight;
            const outputDiv = item.querySelector('.cmd-output');
            try {
                const res = await fetch('/' + encodeURIComponent(cmd));
                const text = await res.text();
                outputDiv.textContent = text || '(no output)';
                if (!res.ok) outputDiv.classList.add('error');
            } catch (err) {
                outputDiv.textContent = '[ERR_CODE_X9] ' + err.message;
                outputDiv.classList.add('error');
            }
            terminal.scrollTop = terminal.scrollHeight;
        }

        async function executeManCommand(fullCmd) {
            const cmdName = cleanCmdName(fullCmd);
            const item = document.createElement('div');
            item.className = 'history-item';
            item.innerHTML = `<div class="cmd-line"><span class="cmd-prompt">user@flux ~ $</span> <span class="cmd-text">${fullCmd}</span></div><div class="man-opened-notice"><span>Loaded documentation for <strong>${cmdName}(1)</strong> in manual panel.</span><button class="btn-notice" onclick="openManContent('${cmdName}')">View</button></div>`;
            terminal.appendChild(item);
            terminal.scrollTop = terminal.scrollHeight;
            openManContent(cmdName);
        }

        function handleFormSubmit(e) {
            e.preventDefault();
            const cmd = cmdInput.value;
            cmdInput.value = '';
            runCommand(cmd);
        }

        function highlightNode(nodeId) {
            document.querySelectorAll('.api-node').forEach(n => n.classList.remove('highlight'));
            document.querySelectorAll('.api-endpoint').forEach(ep => ep.classList.remove('active'));
            const node = document.getElementById(nodeId);
            if (node) node.classList.add('highlight');
            event.currentTarget.classList.add('active');
        }

        const logMessages = ['[SYS] heartbeat ok','[NET] dns resolve 1.2ms','[MEM] heap: 42MB / 256MB','[CPU] load avg: 0.12','[SYS] gc cycle 0.8ms','[NET] tls handshake 3.4ms','[SYS] cache hit ratio 94.2%','[MEM] page fault rate 0.01%','[NET] conn pool: 12/64 active','[SYS] uptime 14d 7h 22m','[CPU] thread count: 8','[NET] bytes rx 1.2GB tx 340MB'];
        let logInterval;
        const sysLogs = document.getElementById('sysLogs');
        const logCell = document.getElementById('logCell');

        function addLogEntry() {
            const msg = logMessages[Math.floor(Math.random() * logMessages.length)];
            const now = new Date();
            const ts = String(now.getHours()).padStart(2,'0') + ':' + String(now.getMinutes()).padStart(2,'0') + ':' + String(now.getSeconds()).padStart(2,'0');
            const entry = document.createElement('div');
            entry.className = 'log-entry';
            entry.innerHTML = '<span class="log-ts">' + ts + '</span> ' + msg;
            sysLogs.appendChild(entry);
            while (sysLogs.children.length > 4) sysLogs.removeChild(sysLogs.firstChild);
        }
        function startLogs() { addLogEntry(); logInterval = setInterval(addLogEntry, 5000); }
        logCell.addEventListener('mouseenter', () => clearInterval(logInterval));
        logCell.addEventListener('mouseleave', () => { logInterval = setInterval(addLogEntry, 5000); });
        document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && panelState === 'content') showManList(); });

        renderManuals();
        startLogs();
    </script>
</body>
</html>
"""

def clean_cmd_name(cmd):
    if not cmd:
        return 'intro'
    c = str(cmd).strip()
    if c.lower().startswith('man '):
        c = c[4:].strip()
    c = re.sub(r'[^a-zA-Z0-9_\\-]', '', c)
    return c or 'intro'

def escape_tex_string(text):
    if not text:
        return ""
    # Encode to clean ASCII for TeX compatibility
    s = text.encode('ascii', errors='ignore').decode('ascii')
    s = s.replace('\\', ' ')
    for char in ['&', '%', '$', '#', '_', '{', '}']:
        s = s.replace(char, '\\' + char)
    s = s.replace('~', ' ')
    s = s.replace('^', ' ')
    return s

def run_shell_command(command_str):
    try:
        res = subprocess.run(
            ['/bin/sh', '-c', command_str],
            capture_output=True,
            timeout=30
        )
        # Strip backspaces (.\x08) used in roff/man pages for bold/underline
        output = re.sub(r'.\x08', '', res.stdout.decode('utf-8', errors='replace'))
        stderr_out = re.sub(r'.\x08', '', res.stderr.decode('utf-8', errors='replace'))

        combined = output
        if stderr_out:
            if combined:
                combined += "\n" + stderr_out
            else:
                combined = stderr_out

        # Smart fallback for "man <cmd>" when man page entry is missing
        if ("No entry for" in combined or not combined.strip() or res.returncode != 0) and command_str.strip().startswith("man "):
            parts = command_str.strip().split()
            if len(parts) >= 2:
                target_cmd = parts[-1]
                fallback_res = subprocess.run(
                    ['/bin/sh', '-c', f"{target_cmd} --help"],
                    capture_output=True,
                    timeout=10
                )
                fallback_out = fallback_res.stdout.decode('utf-8', errors='replace') or fallback_res.stderr.decode('utf-8', errors='replace')
                fallback_clean = re.sub(r'.\x08', '', fallback_out).strip()
                
                if fallback_clean and "command not found" not in fallback_clean.lower():
                    combined = f"{target_cmd.upper()}(1)                       General Commands Manual                      {target_cmd.upper()}(1)\n\nNAME\n     {target_cmd} – command usage & help\n\nSYNOPSIS\n     {target_cmd} [OPTIONS]\n\nDESCRIPTION\n" + fallback_clean
                else:
                    combined = f"{target_cmd.upper()}(1)                       General Commands Manual                      {target_cmd.upper()}(1)\n\nNAME\n     {target_cmd} – command usage & manual\n\nSYNOPSIS\n     {target_cmd} [OPTIONS] [ARGUMENTS...]\n\nDESCRIPTION\n     {target_cmd} is a standard Unix/Linux command-line utility.\n\nOPTIONS\n     -h, --help    Display help information\n     -v, --verbose Enable verbose execution logging\n"

        return res.returncode, combined
    except subprocess.TimeoutExpired:
        return 504, "Error: Command execution timed out (30s limit)\n"
    except Exception as e:
        return 500, f"Error executing command: {str(e)}\n"

def generate_latex_and_pdf(cmd_name):
    os.makedirs(PDF_DIR, exist_ok=True)
    clean_cmd = clean_cmd_name(cmd_name)
    tex_path = os.path.join(PDF_DIR, f"{clean_cmd}.tex")
    pdf_path = os.path.join(PDF_DIR, f"{clean_cmd}.pdf")

    # 1. Check if cached PDF already exists
    if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
        return tex_path, pdf_path

    # 2. Build LaTeX document & try pdflatex
    pdflatex_bin = "/Library/TeX/texbin/pdflatex"
    if not os.path.exists(pdflatex_bin):
        pdflatex_bin = shutil.which("pdflatex")

    _, raw_man = run_shell_command(f"man {clean_cmd}")
    sections = re.split(r'\n(?=[A-Z][A-Z\s]{2,}\n)', raw_man)
    parsed = {}
    for sec in sections:
        lines = sec.strip().split('\n')
        if not lines:
            continue
        hdr = lines[0].strip()
        cnt = '\n'.join(lines[1:])
        if hdr:
            parsed[hdr] = cnt

    tex_lines = [
        r"\documentclass[10pt,a4paper]{article}",
        r"\usepackage[margin=0.75in]{geometry}",
        r"\usepackage{xcolor}",
        r"\usepackage{fancyhdr}",
        r"\usepackage{hyperref}",
        r"\definecolor{brandcyan}{HTML}{008080}",
        r"\definecolor{brandblue}{HTML}{1A5276}",
        r"\pagestyle{fancy}",
        r"\fancyhf{}",
        r"\lhead{\small\textbf{" + clean_cmd.upper() + r"(1) Manual Page}}",
        r"\rhead{\small\textbf{Alpine / Linux Technical Manual}}",
        r"\cfoot{\thepage}",
        r"\hypersetup{colorlinks=true,linkcolor=brandblue,urlcolor=brandcyan,pdftitle={" + clean_cmd + r"(1) Manual Page}}",
        r"\begin{document}",
        r"\noindent",
        r"{\Huge \textbf{\color{brandblue} " + clean_cmd.upper() + r"(1)}} \hfill {\large \textbf{\color{brandcyan} USER COMMANDS}}\\[0.5em]",
        r"{\Large \textbf{" + escape_tex_string(clean_cmd) + r" --- Technical Manual}}\\[0.3em]",
        r"\small\textcolor{gray}{Compiled from Unix Manual System}",
        r"\vspace{1em}",
        r"\hrule",
        r"\vspace{1em}"
    ]

    for hdr, cnt in parsed.items():
        if 'Manual' in hdr or '(1)' in hdr:
            continue
        clean_hdr = escape_tex_string(hdr)
        clean_cnt = cnt.encode('ascii', errors='ignore').decode('ascii')
        tex_lines.append(r"\section*{\color{brandblue} " + clean_hdr + r"}")
        tex_lines.append(r"\begin{verbatim}")
        tex_lines.append(clean_cnt.strip())
        tex_lines.append(r"\end{verbatim}")
        tex_lines.append("\n")

    tex_lines.append(r"\end{document}")
    full_tex = "\n".join(tex_lines)

    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(full_tex)

    if pdflatex_bin:
        try:
            subprocess.run(
                [pdflatex_bin, "-interaction=batchmode", f"-output-directory={PDF_DIR}", tex_path],
                capture_output=True,
                timeout=15
            )
        except Exception:
            pass

    # 3. Fallback: If pdflatex failed or was unavailable, use mandoc -Tpdf
    if not (os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0):
        try:
            res = subprocess.run(
                ['/bin/sh', '-c', f"man -Tpdf {clean_cmd} || mandoc -Tpdf /usr/share/man/man1/{clean_cmd}.1 2>/dev/null"],
                capture_output=True,
                timeout=10
            )
            if res.returncode == 0 and res.stdout:
                with open(pdf_path, 'wb') as f:
                    f.write(res.stdout)
        except Exception:
            pass

    return tex_path, pdf_path

class ShellHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        raw_path = parsed.path
        
        # Normalize path
        if raw_path.startswith('/'):
            raw_path = raw_path[1:]
        
        raw_path = urllib.parse.unquote(raw_path)

        # Serve Web UI for empty path / index.html
        if not raw_path or raw_path.lower() in ('index.html', 'favicon.ico'):
            if raw_path.lower() == 'favicon.ico':
                self.send_response(204)
                self.end_headers()
                return

            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode('utf-8'))
            return

        # Route PDF endpoints: /pdf/{cmd}
        if raw_path.startswith('pdf/'):
            cmd_target = clean_cmd_name(raw_path[4:].strip())
            try:
                _, pdf_file = generate_latex_and_pdf(cmd_target)
                if os.path.exists(pdf_file) and os.path.getsize(pdf_file) > 0:
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/pdf')
                    self.send_header('Content-Disposition', f'inline; filename="{cmd_target}.pdf"')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    with open(pdf_file, 'rb') as f:
                        self.wfile.write(f.read())
                    return
                else:
                    self.send_response(500)
                    self.send_header('Content-Type', 'text/plain; charset=utf-8')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(b"Error: PDF compilation failed or unavailable\n")
                    return
            except Exception as err:
                self.send_response(500)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(f"Error generating PDF: {str(err)}\n".encode('utf-8'))
                return



        # Route manual text requests: /man/{cmd} or /man {cmd}
        if raw_path.startswith('man/') or raw_path.startswith('man '):
            cmd_target = clean_cmd_name(raw_path)
            code, output = run_shell_command(f"man {cmd_target}")
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(output.encode('utf-8'))
            return

        # Execute general shell command
        code, output = run_shell_command(raw_path)
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(output.encode('utf-8'))

    def do_POST(self):
        # Support POST to execute command in request body as well
        content_length = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_length).decode('utf-8', errors='replace').strip()
        
        if not post_body:
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(b"Error: Empty request body\n")
            return

        code, output = run_shell_command(post_body)
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(output.encode('utf-8'))

    def log_message(self, format, *args):
        # Print standard clean log to stderr
        sys.stderr.write("%s - - [%s] %s\n" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format%args))

def run_server(port=3000):
    server_address = ('0.0.0.0', port)
    httpd = ThreadingHTTPServer(server_address, ShellHTTPHandler)
    print(f"Alpine Shell HTTP Server listening on http://0.0.0.0:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()

if __name__ == '__main__':
    port = 3000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run_server(port)
