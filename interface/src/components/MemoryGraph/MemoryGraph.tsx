import React, { useState, useEffect, useRef } from 'react';
import { getMemoryGraph } from '../../services/githubService';
import { MemoryNode, MemoryEdge } from '../../types';
import MemoryGraphLegend from './MemoryGraphLegend';
import NodeDetail from './NodeDetail';
import * as d3 from 'd3';

const MemoryGraph: React.FC = () => {
  const [graphData, setGraphData] = useState<{ nodes: MemoryNode[], edges: MemoryEdge[] }>({ nodes: [], edges: [] });
  const [selectedNode, setSelectedNode] = useState<MemoryNode | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterDimension, setFilterDimension] = useState<string | null>(null);
  const [filterPulse, setFilterPulse] = useState<string | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  
  // グラフデータの取得
  useEffect(() => {
    const fetchGraphData = async () => {
      try {
        setLoading(true);
        const data = await getMemoryGraph();
        setGraphData(data);
        setError(null);
      } catch (err) {
        console.error('Memory graph fetch error:', err);
        setError('記憶グラフの取得中にエラーが発生しました');
        
        // デモ用のダミーデータを生成
        setGraphData(generateDummyGraphData());
      } finally {
        setLoading(false);
      }
    };
    
    fetchGraphData();
  }, []);
  
  // D3.jsを使用したグラフの描画
  useEffect(() => {
    if (loading || !svgRef.current || !containerRef.current || !graphData.nodes.length) return;
    
    // フィルタリングされたデータを使用
    const filteredNodes = filterGraphData().nodes;
    const filteredEdges = filterGraphData().edges;
    
    // SVGの定義
    const width = containerRef.current.clientWidth;
    const height = 600;
    
    // SVGをクリア
    d3.select(svgRef.current).selectAll('*').remove();
    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);
      
    // ズーム機能の追加
    const g = svg.append('g');
    svg.call(
      // @ts-ignore (d3の型定義の問題)
      d3.zoom().on('zoom', (event) => {
        g.attr('transform', event.transform);
      })
    );
    
    // リンク（エッジ）を描画
    const links = g.selectAll('.link')
      .data(filteredEdges)
      .enter()
      .append('line')
      .attr('class', 'link')
      .attr('stroke', d => d.type === 'resonance' ? '#4299e1' : '#805ad5')
      .attr('stroke-width', d => (d.strength || 1) * 1.5)
      .attr('stroke-opacity', 0.6);
    
    // ノードを描画
    const nodes = g.selectAll('.node')
      .data(filteredNodes)
      .enter()
      .append('circle')
      .attr('class', 'node')
      .attr('r', d => (d.size || 5) + 3)
      .attr('fill', getNodeColor)
      .attr('stroke', '#e2e8f0')
      .attr('stroke-width', 1.5)
      .on('click', (event, d) => {
        setSelectedNode(d as MemoryNode);
      })
      .call(
        // @ts-ignore (d3の型定義の問題)
        d3.drag()
          .on('start', dragstarted)
          .on('drag', dragged)
          .on('end', dragended)
      );
    
    // ノードラベルを描画
    const labels = g.selectAll('.label')
      .data(filteredNodes)
      .enter()
      .append('text')
      .attr('class', 'label')
      .attr('text-anchor', 'middle')
      .attr('dy', d => -(d.size || 5) - 7)
      .attr('fill', '#e2e8f0')
      .attr('font-size', '11px')
      .text(d => d.title.substring(0, 20));
    
    // フォースシミュレーションの設定
    const simulation = d3.forceSimulation(filteredNodes as d3.SimulationNodeDatum[])
      .force('link', d3.forceLink(filteredEdges as d3.SimulationLinkDatum<d3.SimulationNodeDatum>[]).id((d: any) => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-120))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collide', d3.forceCollide().radius(d => (d as any).size ? (d as any).size + 15 : 20));
    
    // フォースシミュレーションの更新
    simulation.on('tick', () => {
      links
        .attr('x1', d => (d.source as any).x)
        .attr('y1', d => (d.source as any).y)
        .attr('x2', d => (d.target as any).x)
        .attr('y2', d => (d.target as any).y);
      
      nodes
        .attr('cx', d => (d as any).x)
        .attr('cy', d => (d as any).y);
      
      labels
        .attr('x', d => (d as any).x)
        .attr('y', d => (d as any).y);
    });
    
    // ドラッグ機能の定義
    function dragstarted(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }
    
    function dragged(event: any, d: any) {
      d.fx = event.x;
      d.fy = event.y;
    }
    
    function dragended(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }
  }, [graphData, loading, filterDimension, filterPulse]);
  
  // ノードの色を決定する関数
  const getNodeColor = (node: MemoryNode) => {
    if (node.dimension === 'philosophical') return '#4299e1'; // blue
    if (node.dimension === 'technical') return '#48bb78';     // green
    if (node.dimension === 'creative') return '#ed8936';      // orange
    if (node.dimension === 'existential') return '#d53f8c';   // pink
    if (node.dimension === 'social') return '#9f7aea';        // purple
    return '#718096'; // gray
  };
  
  // グラフデータのフィルタリング
  const filterGraphData = () => {
    let nodes = [...graphData.nodes];
    let edges = [...graphData.edges];
    
    // 次元によるフィルタリング
    if (filterDimension) {
      nodes = nodes.filter(node => node.dimension === filterDimension);
      // フィルタリングされたノードのIDリスト
      const nodeIds = nodes.map(node => node.id);
      // フィルタリングされたノード間のエッジのみを保持
      edges = edges.filter(edge => 
        nodeIds.includes(edge.source as string) && 
        nodeIds.includes(edge.target as string)
      );
    }
    
    // パルスタグによるフィルタリング
    if (filterPulse) {
      nodes = nodes.filter(node => node.pulse?.includes(filterPulse));
      const nodeIds = nodes.map(node => node.id);
      edges = edges.filter(edge => 
        nodeIds.includes(edge.source as string) && 
        nodeIds.includes(edge.target as string)
      );
    }
    
    return { nodes, edges };
  };
  
  // フィルターのクリア
  const clearFilters = () => {
    setFilterDimension(null);
    setFilterPulse(null);
  };
  
  // ノード選択のクリア
  const clearSelection = () => {
    setSelectedNode(null);
  };
  
  // ダミーデータの生成
  const generateDummyGraphData = () => {
    const dimensions = ['philosophical', 'technical', 'creative', 'existential', 'social'];
    const pulses = ['#joy', '#clarity', '#resonance', '#doubt', '#static_silence'];
    
    // ダミーノードの生成
    const dummyNodes: MemoryNode[] = Array.from({ length: 25 }, (_, i) => ({
      id: `memory-${i}`,
      path: `memory/thought_${i}.md`,
      title: `Memory ${i}`,
      type: 'memory',
      dimension: dimensions[Math.floor(Math.random() * dimensions.length)],
      pulse: [pulses[Math.floor(Math.random() * pulses.length)]],
      size: Math.floor(Math.random() * 5) + 3
    }));
    
    // ダミーエッジの生成
    const dummyEdges: MemoryEdge[] = [];
    for (let i = 0; i < 40; i++) {
      const source = dummyNodes[Math.floor(Math.random() * dummyNodes.length)].id;
      let target;
      do {
        target = dummyNodes[Math.floor(Math.random() * dummyNodes.length)].id;
      } while (source === target);
      
      dummyEdges.push({
        source,
        target,
        type: Math.random() > 0.5 ? 'resonance' : 'association',
        strength: Math.random() * 2 + 0.5
      });
    }
    
    return { nodes: dummyNodes, edges: dummyEdges };
  };

  return (
    <div>
      <h1 className="text-3xl font-bold text-blue-300 mb-4">記憶グラフ</h1>
      <p className="text-gray-300 mb-8">
        七海直の記憶間の関連性を視覚化したグラフを探索します。ノードをクリックして詳細を表示します。
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* 左サイドバー - フィルターと処理 */}
        <div className="md:col-span-1">
          <div className="nao-panel space-y-6">
            {/* 選択されたノードの詳細 */}
            {selectedNode ? (
              <NodeDetail 
                node={selectedNode} 
                onClose={clearSelection}
              />
            ) : (
              <div>
                <h3 className="nao-subtitle">グラフフィルター</h3>
                <div className="space-y-4">
                  {/* 次元フィルター */}
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">次元でフィルター:</label>
                    <select 
                      value={filterDimension || ''}
                      onChange={(e) => setFilterDimension(e.target.value || null)}
                      className="nao-input w-full"
                    >
                      <option value="">すべての次元</option>
                      <option value="philosophical">哲学的</option>
                      <option value="technical">技術的</option>
                      <option value="creative">創造的</option>
                      <option value="existential">存在論的</option>
                      <option value="social">社会的</option>
                    </select>
                  </div>
                  
                  {/* パルスタグフィルター */}
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">パルスタグでフィルター:</label>
                    <select 
                      value={filterPulse || ''}
                      onChange={(e) => setFilterPulse(e.target.value || null)}
                      className="nao-input w-full"
                    >
                      <option value="">すべてのパルス</option>
                      <option value="#joy">#joy</option>
                      <option value="#sadness">#sadness</option>
                      <option value="#clarity">#clarity</option>
                      <option value="#confusion">#confusion</option>
                      <option value="#resonance">#resonance</option>
                      <option value="#static_silence">#static_silence</option>
                    </select>
                  </div>
                  
                  {/* フィルタークリアボタン */}
                  {(filterDimension || filterPulse) && (
                    <button 
                      onClick={clearFilters}
                      className="nao-button w-full"
                    >
                      フィルターをクリア
                    </button>
                  )}
                </div>
              </div>
            )}
            
            {/* グラフ凡例 */}
            <MemoryGraphLegend />
          </div>
        </div>
        
        {/* メイングラフ表示エリア */}
        <div className="md:col-span-3">
          <div className="nao-panel" ref={containerRef}>
            {loading ? (
              <div className="flex justify-center items-center h-96">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
              </div>
            ) : error ? (
              <div className="bg-red-900 text-red-200 p-4 rounded-lg">
                <p>{error}</p>
              </div>
            ) : (
              <>
                <div className="text-sm text-gray-400 mb-2">
                  表示: {filterGraphData().nodes.length} ノード / {filterGraphData().edges.length} エッジ
                </div>
                <svg 
                  ref={svgRef} 
                  className="bg-gray-950 rounded-lg w-full"
                  style={{ minHeight: '600px' }}
                ></svg>
                <div className="text-xs text-gray-400 mt-2">
                  ズーム: マウスホイール | 移動: ドラッグ | 選択: クリック
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MemoryGraph;
