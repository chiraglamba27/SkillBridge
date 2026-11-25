import React, { useEffect, useRef, useState } from 'react';
import { Network } from 'vis-network';
import { Maximize2, RotateCcw, Search, ExternalLink, X } from 'lucide-react';

export default function KnowledgeGraph({ graphData, targetRole }) {
  const containerRef = useRef(null);
  const networkRef = useRef(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterResults, setFilterResults] = useState([]);

  useEffect(() => {
    if (!containerRef.current || !graphData || !graphData.nodes) return;

    const data = {
      nodes: graphData.nodes.map((node) => {
        const isKnown = node.node_type === 'known' || node.status === 'Verified' || node.status === 'Verified on Resume';
        const isRec = node.node_type === 'recommended' || node.status === 'Recommended' || node.status === 'Top Recommended Next Step';
        const isSecondary = node.node_type === 'secondary' || node.status === 'Secondary Recommendation';

        let bg = '#14130F';
        let border = '#C8412B';
        let borderWidth = 2.5;

        if (isRec) {
          bg = '#D99A1E';
          border = '#FBF9F4';
          borderWidth = 3.5;
        } else if (isSecondary) {
          bg = '#D99A1E';
          border = '#D99A1E';
          borderWidth = 2;
        } else if (isKnown) {
          bg = '#1F6B4F';
          border = '#1F6B4F';
          borderWidth = 2;
        }

        return {
          id: node.id,
          label: node.label,
          category: node.category,
          demand: node.demand,
          est_weeks: node.est_weeks,
          status: node.status,
          node_type: node.node_type,
          resource_url: node.resource_url,
          resource_title: node.resource_title,
          connections_to_user_skills: node.connections_to_user_skills || [],
          shape: 'dot',
          size: node.size || 20,
          color: {
            background: bg,
            border: border,
            highlight: {
              background: bg,
              border: '#FBF9F4',
            },
            hover: {
              background: bg,
              border: '#FBF9F4',
            },
          },
          borderWidth: borderWidth,
          font: {
            color: '#FBF9F4',
            size: 14,
            strokeWidth: 4,
            strokeColor: '#14130F',
            face: 'IBM Plex Sans, sans-serif',
            bold: true,
          },
          shadow: {
            enabled: true,
            color: 'rgba(0,0,0,0.5)',
            size: 8,
          },
        };
      }),
      edges: graphData.edges.map((edge) => ({
        from: edge.from,
        to: edge.to,
        value: edge.value || 1,
        title: `Co-occurrences: ${edge.value || 1}`,
        color: {
          color: 'rgba(217, 211, 196, 0.22)',
          highlight: 'rgba(243, 239, 230, 0.85)',
          hover: 'rgba(243, 239, 230, 0.85)',
        },
        width: Math.min(4, Math.max(1, (edge.value || 1) * 0.4)),
        smooth: {
          type: 'continuous',
        },
      })),
    };

    const options = {
      nodes: {
        scaling: {
          min: 16,
          max: 36,
        },
      },
      physics: {
        barnesHut: {
          gravitationalConstant: -4200,
          centralGravity: 0.25,
          springLength: 160,
          springConstant: 0.04,
          damping: 0.12,
        },
        stabilization: {
          enabled: true,
          iterations: 140,
        },
      },
      interaction: {
        hover: true,
        tooltipDelay: 100,
        zoomView: true,
        dragView: true,
      },
    };

    const network = new Network(containerRef.current, data, options);
    networkRef.current = network;

    // Freeze physics upon stabilization to prevent perpetual jitter
    network.on('stabilizationIterationsDone', () => {
      network.setOptions({ physics: false });
    });

    // Node selection event
    network.on('click', (params) => {
      if (params.nodes.length > 0) {
        const nodeId = params.nodes[0];
        const nodeObj = data.nodes.find((n) => n.id === nodeId);
        setSelectedNode(nodeObj || null);
      } else {
        setSelectedNode(null);
      }
    });

    return () => {
      if (networkRef.current) {
        networkRef.current.destroy();
        networkRef.current = null;
      }
    };
  }, [graphData]);

  // Search filter
  useEffect(() => {
    if (!searchQuery.trim() || !graphData || !graphData.nodes) {
      setFilterResults([]);
      return;
    }
    const q = searchQuery.toLowerCase();
    const matches = graphData.nodes
      .filter((n) => n.id.toLowerCase().includes(q))
      .slice(0, 6);
    setFilterResults(matches);
  }, [searchQuery, graphData]);

  const handleSelectSearchResult = (nodeId) => {
    if (!networkRef.current || !graphData) return;
    networkRef.current.focus(nodeId, {
      scale: 1.3,
      animation: { duration: 600, easingFunction: 'easeInOutQuad' },
    });
    networkRef.current.selectNodes([nodeId]);
    const nodeObj = graphData.nodes.find((n) => n.id === nodeId);
    setSelectedNode(nodeObj || null);
    setSearchQuery('');
    setFilterResults([]);
  };

  const handleFit = () => {
    if (networkRef.current) {
      networkRef.current.fit({ animation: { duration: 500, easingFunction: 'easeInOutQuad' } });
    }
  };

  const handleRelayout = () => {
    if (networkRef.current) {
      networkRef.current.setOptions({ physics: true });
      setTimeout(() => {
        if (networkRef.current) networkRef.current.setOptions({ physics: false });
      }, 1500);
    }
  };

  return (
    <div className="border border-rule bg-surface overflow-hidden">
      {/* Docked Legend & Controls Bar (Warm Paper Surface) */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-3 border-b border-rule bg-surface px-4 py-2.5">
        {/* Cartographic Shapes Legend */}
        <div className="flex flex-wrap items-center gap-5 text-xs">
          <span className="font-mono text-[11px] uppercase tracking-wider text-ink-muted">Map Legend:</span>
          <div className="flex items-center gap-1.5">
            <span className="inline-block h-3 w-3 rounded-full bg-known"></span>
            <span className="font-mono text-[11px] text-ink">Verified (Filled)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="inline-block h-3 w-3 rounded-full border-2 border-missing bg-[#14130F]"></span>
            <span className="font-mono text-[11px] text-ink">Missing (Hollow Ring)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="inline-block h-3 w-3 rounded-full bg-saffron ring-2 ring-saffron/40"></span>
            <span className="font-mono text-[11px] text-ink">Recommended (Saffron)</span>
          </div>
        </div>

        {/* Search & Canvas Tools */}
        <div className="flex items-center gap-2 w-full md:w-auto">
          {/* Node Search Box */}
          <div className="relative flex-1 md:w-56">
            <div className="flex items-center border border-rule bg-surface-raised px-2.5 py-1 text-xs">
              <Search className="h-3.5 w-3.5 text-ink-muted mr-1.5" />
              <input
                type="text"
                placeholder="Find skill node..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-transparent text-xs text-ink placeholder-ink-muted focus:outline-none font-mono"
              />
              {searchQuery && (
                <button onClick={() => setSearchQuery('')} className="text-ink-muted hover:text-ink">
                  <X className="h-3 w-3" />
                </button>
              )}
            </div>

            {/* Search Dropdown */}
            {filterResults.length > 0 && (
              <div className="absolute top-full left-0 right-0 z-30 mt-1 border border-rule bg-surface-raised shadow-lift">
                {filterResults.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => handleSelectSearchResult(item.id)}
                    className="flex w-full items-center justify-between px-3 py-1.5 text-left text-xs hover:bg-paper font-mono"
                  >
                    <span className="text-ink font-semibold">{item.label}</span>
                    <span className="text-[10px] text-ink-muted">{item.category}</span>
                  </button>
                ))}
              </div>
            )}
          </div>

          <button
            onClick={handleFit}
            className="border border-rule bg-surface-raised px-2.5 py-1 text-xs text-ink hover:bg-paper font-mono transition"
            title="Fit view to show all nodes"
          >
            Fit View
          </button>
          <button
            onClick={handleRelayout}
            className="border border-rule bg-surface-raised px-2.5 py-1 text-xs text-ink hover:bg-paper font-mono transition"
            title="Re-run physics layout and freeze"
          >
            Re-layout
          </button>
        </div>
      </div>

      {/* Main Canvas Area (Dark Surface Centerpiece) */}
      <div className="relative bg-canvas-dark">
        <div ref={containerRef} className="h-[600px] w-full cursor-grab active:cursor-grabbing" />

        {/* Docked Node Detail Drawer (Overlay Panel) */}
        {selectedNode && (
          <div className="absolute top-3 right-3 z-20 w-80 max-w-[calc(100%-24px)] border border-rule bg-surface-raised p-4 shadow-dark animate-in fade-in duration-200">
            <div className="flex items-start justify-between border-b border-rule-subtle pb-2.5 mb-3">
              <div>
                <span className="font-mono text-[10px] uppercase tracking-wider text-ink-muted">
                  {selectedNode.category || 'Competency Node'}
                </span>
                <h4 className="font-serif text-xl font-bold text-ink leading-tight">
                  {selectedNode.label || selectedNode.id}
                </h4>
              </div>
              <button
                onClick={() => setSelectedNode(null)}
                className="text-ink-muted hover:text-ink p-1"
                aria-label="Close detail panel"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex items-center justify-between font-mono">
                <span className="text-ink-muted">Status:</span>
                <span
                  className={`font-semibold ${
                    selectedNode.status === 'Verified' || selectedNode.node_type === 'known'
                      ? 'text-known'
                      : selectedNode.status === 'Recommended' || selectedNode.node_type === 'recommended'
                      ? 'text-saffron font-bold'
                      : 'text-missing'
                  }`}
                >
                  {selectedNode.status || 'Role Requirement'}
                </span>
              </div>

              <div className="flex items-center justify-between font-mono">
                <span className="text-ink-muted">Market Demand:</span>
                <span className="text-ink font-bold tabular-nums">
                  {selectedNode.demand ? `${selectedNode.demand}%` : 'Standard'}
                </span>
              </div>

              <div className="flex items-center justify-between font-mono">
                <span className="text-ink-muted">Est. Acquisition:</span>
                <span className="text-ink tabular-nums">
                  ~{selectedNode.est_weeks || 3} weeks
                </span>
              </div>

              {/* Connections to candidate verified skills */}
              {selectedNode.connections_to_user_skills && selectedNode.connections_to_user_skills.length > 0 && (
                <div className="border-t border-rule-subtle pt-2 mt-2">
                  <span className="font-mono text-[10px] uppercase tracking-wider text-ink-muted block mb-1.5">
                    Co-occurrence with Your Skills:
                  </span>
                  <div className="space-y-1 max-h-28 overflow-y-auto pr-1">
                    {selectedNode.connections_to_user_skills.map((c, i) => (
                      <div key={i} className="flex justify-between font-mono text-[11px] text-ink py-0.5 border-b border-rule-subtle/50">
                        <span>{c.skill}</span>
                        <span className="text-ink-muted tabular-nums">wt {c.weight}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Curated Resource Link */}
              {selectedNode.resource_url && (
                <div className="border-t border-rule-subtle pt-2.5">
                  <a
                    href={selectedNode.resource_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 text-cobalt font-semibold hover:underline"
                  >
                    <span>{selectedNode.resource_title || 'Documentation reference'}</span>
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
