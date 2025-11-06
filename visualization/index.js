// Format duration in seconds to human readable format
function formatDuration(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  } else if (minutes > 0) {
    return `${minutes}m ${secs}s`;
  } else {
    return `${secs}s`;
  }
}

async function getCategoriesAndColors(client) {
  try {
    const classes = await client.get_setting("classes");
    const theme = await client.get_setting("theme");

    // Helper function to find color by iterating up the hierarchy
    function findColorInHierarchy(namePath, classes) {
      // Start from the current level and go up the hierarchy
      for (let i = namePath.length; i > 0; i--) {
        const ancestorPath = namePath.slice(0, i).join(' > ');
        const ancestorClass = classes.find(c => c.name.join(' > ') === ancestorPath);
        if (ancestorClass && ancestorClass.data && ancestorClass.data.color) {
          return ancestorClass.data.color;
        }
      }
      return null;
    }

    // Build colors dictionary: { "Category > Path": "#HEX" }
    // Classes inherit color from any ancestor in the hierarchy
    const colors = {};
    classes.forEach(cls => {
      const categoryPath = cls.name.join(' > ');
      const inheritedColor = findColorInHierarchy(cls.name, classes);
      if (inheritedColor) {
        colors[categoryPath] = inheritedColor;
      }
    });

    return {colors, theme};
  } catch (error) {
    console.error('Error loading categories and theme from client:', error);
    return {
      colors: {},
      theme: 'light'
    };
  }
}

let categoryColors = {};

// Main function to load and render the chart
async function loadAndRenderChart() {
  const urlParams = new URLSearchParams(window.location.search);
  const hostname = urlParams.get('hostname');
  const start = urlParams.get('start');
  const end = urlParams.get('end');

  if (!hostname || !start || !end) {
    console.error('Missing required URL parameters: hostname, start, end');
    return;
  }

  // Create AW client
  const client = new AWClient('aw-watcher-nextblock', {baseURL: window.location.origin});

  try {
    // Load colors and theme from client settings
    const {colors, theme} = await getCategoriesAndColors(client);
    categoryColors = colors; // Store colors globally for getCategoryColor()

    // Apply theme to the page
    const backgroundColor = theme === 'dark' ? '#1A1D24' : '#FFFFFF';
    const textColor = theme === 'dark' ? '#FFFFFF' : '#000000';
    document.body.style.backgroundColor = backgroundColor;
    document.body.style.color = textColor;
    document.getElementById('chart-container').style.backgroundColor = backgroundColor;

    // Query nextblock events (task blocks)
    const bid_nextblock = `aw-watcher-nextblock_${hostname}`;
    const bid_afk = `aw-watcher-afk_${hostname}`;
    const bid_window = `aw-watcher-window_${hostname}`;

    // Get nextblock events to define blocks
    const nextblockQuery = `RETURN = query_bucket("${bid_nextblock}");`;
    const nextblockData = await client.query([`${start}/${end}`], [nextblockQuery]);
    const nextblockEvents = nextblockData[0] || [];

    if (nextblockEvents.length === 0) {
      document.getElementById('no-data').style.display = 'block';
      document.getElementById('loading').style.display = 'none';
      return;
    }

    // Get categories from classes
    const classes = await client.get_setting("classes");

    // Categorize window events (without filtering AFK)
    const categorizeQuery = `
events = query_bucket("${bid_window}");
events = categorize(events, ${JSON.stringify(classes.map(cls => [cls.name, cls.rule]))});
RETURN = events;
    `;
    const categorizedData = await client.query([`${start}/${end}`], [categorizeQuery]);
    const categorizedEvents = categorizedData[0] || [];

    // Get AFK events to create a separate category
    const afkQuery = `
afk_events = query_bucket("${bid_afk}");
afk = filter_keyvals(afk_events, "status", ["afk"]);
RETURN = afk;
    `;
    const afkData = await client.query([`${start}/${end}`], [afkQuery]);
    const afkEvents = afkData[0] || [];

    // Group nextblock events by block name and sort by timestamp
    const blockMap = {};
    const blockTimestamps = {};
    const blockPlannedDurations = {};

    nextblockEvents.forEach(event => {
      const blockName = event.data.block || 'Unknown';
      if (!blockMap[blockName]) {
        blockMap[blockName] = [];
        blockTimestamps[blockName] = new Date(event.timestamp).getTime();
        blockPlannedDurations[blockName] = event.data.planned_duration * 60 || 0;
      }
      blockMap[blockName].push(event);
    });

    // Sort blocks by timestamp (oldest to newest)
    const blockNames = Object.keys(blockMap).sort((a, b) => {
      return blockTimestamps[a] - blockTimestamps[b];
    });

    const categorySet = new Set();
    categorizedEvents.forEach(event => {
      const category = event.data.$category ?
        event.data.$category.join(' > ') :
        'Uncategorized';
      categorySet.add(category);
    });

    // Add AFK as a category
    if (afkEvents.length > 0) {
      categorySet.add('AFK');
    }

    const categories = Array.from(categorySet).sort();

    // Build datasets for each category
    const datasets = categories.map(category => {
      const data = blockNames.map(blockName => {
        // Get time range for this block
        const blockEvents = blockMap[blockName];
        const blockStart = new Date(blockEvents[0].timestamp).getTime();
        const blockEnd = blockStart + (blockEvents[0].duration * 1000);

        // Handle AFK category separately
        if (category === 'AFK') {
          return afkEvents
            .filter(e => {
              const eventStart = new Date(e.timestamp).getTime();
              const eventEnd = eventStart + (e.duration * 1000);
              return eventStart < blockEnd && eventEnd > blockStart;
            })
            .reduce((sum, e) => sum + e.duration, 0);
        }

        // Handle regular categories
        return categorizedEvents
          .filter(e => {
            const eventCategory = e.data.$category ?
              e.data.$category.join(' > ') :
              'Uncategorized';
            if (eventCategory !== category) return false;

            const eventStart = new Date(e.timestamp).getTime();
            const eventEnd = eventStart + (e.duration * 1000);

            // Check if event overlaps with block
            return eventStart < blockEnd && eventEnd > blockStart;
          })
          .reduce((sum, e) => sum + e.duration, 0);
      });

      return {
        label: category,
        data: data,
        backgroundColor: getCategoryColor(category),
        borderWidth: 0,
        stack: 'actual'
      };
    });

    // Add planned duration dataset
    const plannedData = blockNames.map(blockName => blockPlannedDurations[blockName]);
    datasets.push({
      label: 'Planned Duration',
      data: plannedData,
      backgroundColor: 'rgba(255, 140, 0, 0.7)',
      borderWidth: 0,
      stack: 'planned'
    });

    if (datasets.length === 0) {
      document.getElementById('no-data').style.display = 'block';
      document.getElementById('loading').style.display = 'none';
      return;
    }

    const gridColor = theme === 'dark' ? '#333333' : '#E0E0E0';
    const tickColor = theme === 'dark' ? '#CCCCCC' : '#666666';

    // Calculate total time for each block (excluding Planned Duration)
    const blockTotals = {};
    blockNames.forEach((blockName, index) => {
      let total = 0;
      datasets.forEach((dataset, datasetIndex) => {
        // Skip the 'Planned Duration' dataset
        if (dataset.label !== 'Planned Duration') {
          total += dataset.data[index] || 0;
        }
      });
      blockTotals[blockName] = total;
    });

    const chartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      plugins: {
        tooltip: {
          callbacks: {
            label: function (context) {
              const duration = formatDuration(context.parsed.x);
              const blockName = context.label;
              const totalTime = blockTotals[blockName];
              
              // Show total time for activity datasets (not Planned Duration)
              if (context.dataset.label !== 'Planned Duration') {
                return [
                  `${context.dataset.label}: ${duration}`,
                  `Total: ${formatDuration(totalTime)}`
                ];
              }
              return `${context.dataset.label}: ${duration}`;
            },
            title: function (context) {
              return context[0].label;
            }
          }
        },
        legend: {
          display: false,
        },
      },
      scales: {
        y: {
          stacked: true,
          grid: {
            color: gridColor,
          },
          ticks: {
            color: tickColor,
            autoSkip: false,
          },
        },
        x: {
          stacked: true,
          grid: {
            color: gridColor,
          },
          ticks: {
            callback: function (value) {
              return formatDuration(value);
            },
            color: tickColor,
          },
        },
      },
      layout: {
        padding: {
          top: 10,
          bottom: 10,
          left: 10,
          right: 10
        }
      }
    };

    document.getElementById('loading').style.display = 'none';
    document.getElementById('chart').style.display = 'block';

    // Calculate dynamic height based on number of blocks
    // Each block needs approximately 40-50px of vertical space
    const blockCount = blockNames.length;
    const minHeight = Math.max(250, blockCount * 20 + 100);

    const chartContainer = document.getElementById('chart-container');
    chartContainer.style.minHeight = minHeight + 'px';
    document.body.style.minHeight = minHeight + 'px';
    document.documentElement.style.minHeight = minHeight + 'px';

    const canvas = document.getElementById('chart');
    new Chart(canvas, {
      type: 'bar',
      data: {
        labels: blockNames,
        datasets: datasets
      },
      options: chartOptions,
    });
  } catch (error) {
    console.error('Error loading data:', error);
    document.getElementById('no-data').style.display = 'block';
    document.getElementById('loading').style.display = 'none';
  }
}

function getCategoryColor(category) {
  if (category === 'AFK') {
    return '#888888'; // Gray color for AFK
  }

  if (categoryColors[category]) {
    return categoryColors[category];
  }

  const defaultColors = {
    'Uncategorized': '#CCC'
  };

  return defaultColors[category] || '#6699ff'; // Default blue
}

window.addEventListener('load', loadAndRenderChart);