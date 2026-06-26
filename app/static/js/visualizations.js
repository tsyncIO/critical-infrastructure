function renderDependencyGraph(containerId, apiUrl) {
  const container = document.getElementById(containerId);
  if (!container) return;

  fetch(apiUrl)
    .then((resp) => resp.json())
    .then((data) => {
      const elements = [];
      data.nodes.forEach((node) => {
        elements.push({ data: { id: node.id, label: node.label, sector: node.sector } });
      });
      data.edges.forEach((edge) => {
        elements.push({ data: { id: edge.id, source: edge.source, target: edge.target, label: edge.dependency_type } });
      });

      cytoscape({
        container,
        elements,
        style: [
          {
            selector: 'node',
            style: {
              'label': 'data(label)',
              'text-valign': 'center',
              'color': '#fff',
              'background-color': '#0d6efd',
              'width': 'label',
              'height': 'label',
              'padding': '10',
              'text-wrap': 'wrap',
              'text-max-width': 120,
            },
          },
          {
            selector: 'edge',
            style: {
              'label': 'data(label)',
              'curve-style': 'bezier',
              'target-arrow-shape': 'triangle',
              'target-arrow-color': '#6c757d',
              'line-color': '#6c757d',
              'arrow-scale': 1.2,
              'font-size': 10,
            },
          },
        ],
        layout: {
          name: 'cose',
          idealEdgeLength: 120,
          nodeOverlap: 20,
          refresh: 20,
          fit: true,
        },
      });
    });
}

function renderAlarmTimeSeries(containerId, apiUrl) {
  const container = document.getElementById(containerId);
  if (!container) return;

  fetch(apiUrl)
    .then((resp) => resp.json())
    .then((alarms) => {
      const grouped = {};
      alarms.forEach((alarm) => {
        const key = `${alarm.component_key} - ${alarm.alarm_type}`;
        if (!grouped[key]) grouped[key] = { x: [], y: [], text: [] };
        grouped[key].x.push(alarm.time_step);
        grouped[key].y.push(alarm.deviation_value || 0);
        grouped[key].text.push(alarm.message);
      });

      const traces = Object.entries(grouped).map(([name, series]) => ({
        x: series.x,
        y: series.y,
        mode: 'lines+markers',
        name,
        text: series.text,
        hoverinfo: 'text+y',
      }));

      const layout = {
        title: 'Alarm deviation time series',
        xaxis: { title: 'Time step' },
        yaxis: { title: 'Deviation from threshold' },
        legend: { orientation: 'h', x: 0, y: 1.1 },
        margin: { t: 40, b: 40, l: 60, r: 30 },
      };

      Plotly.newPlot(container, traces, layout, { responsive: true });
    });
}

function renderBpmnViewer(containerId, bpmnFileUrl) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const viewer = new BpmnJS({ container });
  fetch(bpmnFileUrl)
    .then((response) => response.text())
    .then((xml) => viewer.importXML(xml))
    .catch((error) => {
      container.innerHTML = `<div class="alert alert-danger">Failed to load BPMN model: ${error.message}</div>`;
    });
}
