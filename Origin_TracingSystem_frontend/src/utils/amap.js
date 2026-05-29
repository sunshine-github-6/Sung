import { load } from '@amap/amap-jsapi-loader'
import config from '@/config/index'

/**
 * 初始化高德地图
 * @param {HTMLElement} container - 地图容器
 * @param {Object} options - 地图配置选项
 * @returns {Promise<{map: AMap.Map, AMap: Object}>} 返回地图实例和AMap命名空间
 */
export async function initAMap(container, options = {}) {
  // 捕获全局错误，避免控制台报错影响用户体验
  // 提前设置错误处理逻辑，确保能捕获到地图初始化过程中的错误
  let errorHandler = null
  
  // 验证DOM容器
  if (!container) {
    throw new Error('地图容器不存在，请提供有效的DOM元素作为容器')
  }
  
  // 检查容器是否有有效尺寸
  const containerRect = container.getBoundingClientRect();
  if (containerRect.width <= 0 || containerRect.height <= 0) {

    const computedStyle = window.getComputedStyle(container);
    const width = parseFloat(computedStyle.width);
    const height = parseFloat(computedStyle.height);
    
    if (width <= 0 || height <= 0) {

      container.style.width = container.style.width || '400px';
      container.style.height = container.style.height || '300px';
    }
  }
  
  // 从配置文件读取 Key
  const amapKey = config.amap.key
  try {
    // 先设置全局错误处理逻辑
    errorHandler = function(event) {
      const msg = event.message || ''
      // 忽略高德地图的已知错误
      if (msg.includes('USERKEY_PLAT_NOMATCH') ||msg.includes('Unimplemented type: 3') ||msg.includes('FlyDataAuthTask error') ||msg.includes('wf is not a function') ||msg.includes('Failed to execute \'postMessage\' on \'Worker\'') ||msg.includes('DataCloneError')) {

        event.preventDefault() // 阻止错误继续传播
        return true
      }
      return false
    }
    
    // 添加错误事件监听
    window.addEventListener('error', errorHandler)
    
    // 加载高德地图API和插件
    // 使用更稳定的加载方式，避免 PBF 解析错误
    const loadOptions = {
      key: amapKey,
      version: config.amap.version || '2.0',  // 升级到2.0版本以获得更好性能
      plugins: config.amap.plugins || ['AMap.Scale', 'AMap.OverView', 'AMap.MapType', 'AMap.ControlBar', 'AMap.HawkEye', 'AMap.ToolBar', 'AMap.HeatMap'],
      ...config.amap.loaderConfig,  // 使用配置文件中的加载器特定配置
    }
    
    const AMap = await load(loadOptions)
    
    // 默认地图配置
    // 简化配置以避免 "Unimplemented type: 3" 错误
    const defaultOptions = {
      zoom: 5,
      center: [108.0, 34.0],
      viewMode: '2D',
      resizeEnable: true,
      rotateEnable: false, // 禁用旋转以避免某些错误
      pitchEnable: false,  // 禁用俯仰以避免某些错误
      zoomEnable: true,
      dragEnable: true,
      keyboardEnable: true,
      doubleClickZoom: true,
      scrollWheel: true,
      touchZoom: true,
      jogEnable: false,   // 禁用摇杆以避免某些错误
      showLabel: true,
      isHotspot: false,
      crs: 'EPSG3857',
      animateEnable: true,
      // 简化地图要素，避免加载可能导致错误的高级样式
      features: ['bg', 'point', 'road'] // 移除 'building' 以避免样式解析错误
    }
    
    // 创建地图实例
    const map = new AMap.Map(container, { ...defaultOptions, ...options })
    
    // 分步加载插件，单个插件失败不影响整体加载
    // 首先加载核心插件
    const corePlugins = ['Scale', 'OverView', 'MapType'];
    const additionalPlugins = ['ControlBar', 'HawkEye', 'Geolocation', 'ToolBar', 'CloudDataLayer', 'HeatMap'];

    // 验证插件是否真正可用
    const validatePlugin = (pluginName) => {
      if (!AMap[pluginName]) {

        return false;
      }
      
      // 某些插件需要检查构造函数是否存在
      if (typeof AMap[pluginName] !== 'function') {

        return false;
      }
      
      return true;
    };


    // 加载核心控件
    addControlSafely(map, 'Scale', AMap.Scale, {
      position: 'LB', // 左下角
      offset: [10, 10]
    });
    
    addControlSafely(map, 'OverView', AMap.OverView, {
      position: 'RT', // 改到右上角
      offset: [10, 10],
      isOpen: false
    });
    
    addControlSafely(map, 'MapType', AMap.MapType, {
      position: 'LT',
      offset: [10, 50],
      showTraffic: false,
      showRoad: true
    });
    
    // 加载额外控件
    addControlSafely(map, 'ControlBar', AMap.ControlBar, {
      position: 'LB',
      offset: [20, 120] // 调整位置，避免与Scale控件重叠
    });
    
    addControlSafely(map, 'HawkEye', AMap.HawkEye, {
      position: 'RB',
      offset: [10, 120],
      autoMove: true, // 是否随主图视口变化
      showRectangle: true, // 是否显示矩形框
      showButton: true, // 是否显示打开关闭的按钮
      isOpen: false // 是否默认开启
    });
    
    addControlSafely(map, 'Geolocation', AMap.Geolocation, {
      position: 'RB',
      offset: [10, 40], // 调整位置，从原来10改为40
      showCircle: true, // 是否显示定位精度圆
      showButton: true, // 是否显示定位按钮
      buttonPosition: 'RB', // 定位按钮的位置
      buttonOffset: new AMap.Pixel(10, 50), // 定位按钮距离对应角落的偏移量
      zoomToAccuracy: true // 定位成功后是否自动调整地图视野
    });
    
    addControlSafely(map, 'ToolBar', AMap.ToolBar, {
      position: 'RB',
      offset: new AMap.Pixel(10, 10) // 调整位置，从原来100改为10，移到最下方
    });
    
    // 处理云数据图层
    try {
      if (validatePlugin('CloudDataLayer')) {
        // 云数据图层需要有效的数据服务ID
        // 这里只是初始化，实际使用时需要替换为真实的数据服务ID

      }
    } catch (error) {

    }
    
    // 处理热力图
    try {
      if (validatePlugin('HeatMap')) {
        // 热力图需要数据才能显示，这里仅做准备

      }
    } catch (error) {

    }
    
    // 处理行政区划搜索插件
    try {
      if (validatePlugin('DistrictSearch')) {
        // DistrictSearch插件需要数据才能显示，这里仅做准备

      } else {

      }
    } catch (error) {

    }
    
    // 添加自定义控件替代可能失败的原生控件
    setTimeout(() => {
      addCustomControls(map, AMap)
    }, 150) // 稍晚于其他控件加载自定义控件
    
    
    // 地图加载完成事件
    map.on('complete', () => {

    })
    
    // 地图渲染完成事件
    map.on('rendercomplete', () => {

    })
    
    // 添加错误事件监听
    map.on('error', (e) => {

      // 忽略某些不影响使用的错误
      if (e && e.message && (e.message.includes('USERKEY_PLAT_NOMATCH') ||e.message.includes('Unimplemented type') ||e.message.includes('wf is not a function'))) {

        return
      }
    })
    
    // 保存事件监听器引用，以便后续清理
    map.errorHandler = errorHandler
    

    return { map, AMap }
  } catch (error) {

    // 清理错误事件监听器
    if (errorHandler) {
      window.removeEventListener('error', errorHandler)
    }
    // 提供更详细的错误信息
    if (error.message && error.message.includes('Unimplemented type')) {
      throw new Error(`高德地图API版本兼容性问题，请尝试清除浏览器缓存或联系技术支持。原始错误: ${error.message}`)
    }
    if (error.message && error.message.includes('USERKEY_PLAT_NOMATCH')) {
      throw new Error(`高德地图API Key平台类型不匹配。请确保API Key是为Web平台创建的。如需帮助，请联系技术支持。`)
    }
    if (error.message && error.message.includes('wf is not a function')) {
      throw new Error(`高德地图工具条控件存在兼容性问题，已通过自定义控件替代。原始错误: ${error.message}`)
    }
    throw new Error(`高德地图初始化失败: ${error.message}`)
  }
}


/**
 * 创建地图标记点
 * @param {AMap} AMap - AMap命名空间
 * @param {Array} position - 位置坐标 [lng, lat]
 * @param {Object} options - 标记选项
 * @returns {AMap.Marker} 标记实例
 */
export function createMarker(AMap, position, options = {}) {
  const defaultOptions = {
    position: new AMap.LngLat(position[0], position[1]),
    offset: new AMap.Pixel(0, 0),
    icon: null,
    title: options.title || '',
    zIndex: options.zIndex || 100,
    topWhenClick: true, // 点击时置顶
    topWhenMouseOver: false, // 鼠标悬停时置顶
    raiseOnDrag: false, // 拖拽时置顶
    cursor: 'pointer',
    draggable: options.draggable || false,
    visible: true,
    extData: options.extData || null
  }
  
  return new AMap.Marker({ ...defaultOptions, ...options })
}

/**
 * 创建折线
 * @param {AMap} AMap - AMap命名空间
 * @param {Array} path - 路径坐标数组
 * @param {Object} options - 折线选项
 * @returns {AMap.Polyline} 折线实例
 */
export function createPolyline(AMap, path, options = {}) {
  const defaultOptions = {
    path: path.map(coord => new AMap.LngLat(coord[0], coord[1])),
    strokeColor: options.strokeColor || '#3366FF',
    strokeWeight: options.strokeWeight || 4,
    strokeOpacity: options.strokeOpacity || 0.7,
    strokeStyle: options.strokeStyle || 'solid',
    lineJoin: 'round',
    lineCap: 'round',
    isOutline: true,
    outlineColor: 'rgba(255, 255, 255, 0.8)',
    borderWeight: 2,
    zIndex: options.zIndex || 50,
    cursor: 'pointer',
    geodesic: false, // 是否显示为大地线
    showDir: false, // 是否显示方向箭头
    dirColor: '#3366FF',
    dirImg: null
  }
  
  return new AMap.Polyline({ ...defaultOptions, ...options })
}

/**
 * 创建信息窗体
 * @param {AMap} AMap - AMap命名空间
 * @param {Object} options - 信息窗体选项
 * @returns {AMap.InfoWindow} 信息窗体实例
 */
export function createInfoWindow(AMap, options = {}) {
  const defaultOptions = {
    isCustom: false, // 是否自定义窗体
    autoMove: true, // 是否自动调整窗体到视野内
    closeWhenClickMap: true, // 点击地图关闭窗体
    offset: new AMap.Pixel(0, -30),
    position: null,
    size: null,
    content: options.content || '',
    anchor: 'bottom-center'
  }
  
  return new AMap.InfoWindow({ ...defaultOptions, ...options })
}

/**
 * 批量添加覆盖物到地图
 * @param {AMap.Map} map - 地图实例
 * @param {Array} overlays - 覆盖物数组
 */
export function addOverlays(map, overlays) {
  if (!map || !overlays || overlays.length === 0) return
  
  try {
    // 使用批量添加方法提高性能
    map.add(overlays)
  } catch (error) {

    // 如果批量添加失败，逐个添加
    overlays.forEach(overlay => {
      try {
        map.add(overlay)
      } catch (e) {

      }
    })
  }
}

/**
 * 批量移除覆盖物
 * @param {AMap.Map} map - 地图实例
 * @param {Array} overlays - 覆盖物数组
 */
export function removeOverlays(map, overlays) {
  if (!map || !overlays || overlays.length === 0) return
  
  try {
    map.remove(overlays)
  } catch (error) {

    overlays.forEach(overlay => {
      try {
        map.remove(overlay)
      } catch (e) {

      }
    })
  }
}

/**
 * 设置地图视野以适应所有覆盖物
 * @param {AMap.Map} map - 地图实例
 * @param {Array} overlays - 覆盖物数组
 * @param {Object} options - 选项
 */
export function fitView(map, overlays, options = {}) {
  if (!map || !overlays || overlays.length === 0) return
  
  const defaultOptions = {
    immediately: false, // 是否立即执行
    avoid: [20, 20, 20, 20], // 上下左右的避让宽度
    maxZoom: 18 // 最大缩放级别
  }
  
  try {
    map.setFitView(overlays, options.immediately || defaultOptions.immediately, 
                   options.avoid || defaultOptions.avoid, 
                   options.maxZoom || defaultOptions.maxZoom)
  } catch (error) {

  }
}

/**
 * 检查地图控件是否已加载
 * @param {AMap.Map} map - 地图实例
 */
// 添加自定义控件作为工具条的替代
function addCustomControls(map, AMap) {

  
  // 创建缩放控件
  const zoomInBtn = document.createElement('div');
  zoomInBtn.innerHTML = '+';
  zoomInBtn.style.cssText = `
    position: absolute;
    top: 10px;
    right: 10px;
    width: 30px;
    height: 30px;
    background: white;
    border: 1px solid #ccc;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 16px;
    z-index: 1000;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  `;
  
  zoomInBtn.onclick = () => {
    const currentZoom = map.getZoom();
    map.setZoom(currentZoom + 1);
  };
  
  const zoomOutBtn = document.createElement('div');
  zoomOutBtn.innerHTML = '-';
  zoomOutBtn.style.cssText = `
    position: absolute;
    top: 45px;
    right: 10px;
    width: 30px;
    height: 30px;
    background: white;
    border: 1px solid #ccc;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 16px;
    z-index: 1000;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  `;
  
  zoomOutBtn.onclick = () => {
    const currentZoom = map.getZoom();
    map.setZoom(currentZoom - 1);
  };
  
  // 添加到地图容器
  const container = map.getContainer();
  if (container && zoomInBtn && zoomOutBtn) {
    container.appendChild(zoomInBtn);
    container.appendChild(zoomOutBtn);
    
    // 保存对控件的引用以便后续清理
    if (!map.customControls) {
      map.customControls = {};
    }
    map.customControls.zoomInBtn = zoomInBtn;
    map.customControls.zoomOutBtn = zoomOutBtn;
  }
}

// 清理自定义控件和事件监听器
export function cleanupCustomControls(map) {
  if (map) {
    // 移除自定义控件
    if (map.customControls) {
      const container = map.getContainer();
      if (container) {
        // 移除自定义控件
        if (map.customControls.zoomInBtn) {
          container.removeChild(map.customControls.zoomInBtn);
        }
        if (map.customControls.zoomOutBtn) {
          container.removeChild(map.customControls.zoomOutBtn);
        }
      }
      
      // 清空引用
      map.customControls = null;
    }
    
    // 移除错误事件监听器
    if (map.errorHandler) {
      window.removeEventListener('error', map.errorHandler);
      map.errorHandler = null;
    }
  }
}

export function checkControlsLoaded(map) {
  if (!map) {
    console.warn('地图实例不存在')
    return
  }
  







}

// 添加控件的安全函数
const addControlSafely = (map, controlName, controlConstructor, options = {}) => {
  try {
    const AMap = window.AMap; // 从全局获取AMap对象
    if (typeof AMap !== 'undefined' && AMap[controlName]) {
      const control = new AMap[controlName](options);
      map.addControl(control);

      return control;
    } else {

      return null;
    }
  } catch (error) {

    return null;
  }
};

// 添加覆盖物的安全函数
const addOverlaySafely = (map, overlayName, overlayConstructor, options = {}) => {
  try {
    const AMap = window.AMap; // 从全局获取AMap对象
    if (typeof AMap !== 'undefined' && AMap[overlayName]) {
      const overlay = new AMap[overlayName](options);
      overlay.setMap && overlay.setMap(map);

      return overlay;
    } else {

      return null;
    }
  } catch (error) {

    return null;
  }
};

/**
 * 创建栅格图层
 * @param {AMap} AMap - AMap命名空间
 * @param {Object} options - 栅格图层选项
 * @returns {AMap.TileLayer|AMap.ImageLayer} 栅格图层实例
 */
export function createRasterLayer(AMap, options = {}) {
  const { type = 'tile', ...layerOptions } = options;

  try {
    if (type === 'tile') {
      // 创建瓦片图层 - 高德地图 2.0 API
      // 使用 getTileUrl 函数来动态生成瓦片 URL
      const tileUrl = options.tileUrl || options.url || '';

      if (!tileUrl) {
        console.error('瓦片图层 URL 不能为空');
        return null;
      }

      // 构建 getTileUrl 函数
      const getTileUrl = options.getTileUrl || function(x, y, z) {
        // 支持 {x} {y} {z} 占位符的 URL 模板
        return tileUrl
          .replace('{x}', x)
          .replace('{y}', y)
          .replace('{z}', z)
          .replace('{X}', x)
          .replace('{Y}', y)
          .replace('{Z}', z);
      };

      const tileLayerOptions = {
        tileSize: options.tileSize || 256,
        zIndex: options.zIndex || 10,
        opacity: options.opacity ?? 0.7,
        visible: options.visible !== false,
        zooms: options.zooms || [3, 18],
        getTileUrl: getTileUrl
      };

      console.log('创建瓦片图层，配置:', tileLayerOptions);
      return new AMap.TileLayer(tileLayerOptions);
    } else if (type === 'image') {
      // 创建单张图片图层
      if (!options.url) {
        console.error('图片图层 URL 不能为空');
        return null;
      }

      if (!options.bounds) {
        console.error('图片图层需要设置 bounds（地理边界）');
        return null;
      }

      const imageLayerOptions = {
        bounds: options.bounds,
        url: options.url,
        zIndex: options.zIndex || 10,
        opacity: options.opacity ?? 0.7,
        visible: options.visible !== false
      };

      console.log('创建图片图层，配置:', imageLayerOptions);
      return new AMap.ImageLayer(imageLayerOptions);
    }
  } catch (error) {
    console.error('创建栅格图层失败:', error);
    return null;
  }
}

/**
 * 创建热力图图层
 * @param {AMap} AMap - AMap命名空间
 * @param {AMap.Map} map - 地图实例
 * @param {Array} data - 热力图数据
 * @param {Object} options - 热力图选项
 * @returns {AMap.HeatMap} 热力图实例
 */
export function createHeatMap(AMap, map, data = [], options = {}) {
  try {
    console.log('=== createHeatMap 被调用 ===');
    console.log('AMap 对象:', AMap ? '存在' : '不存在');
    console.log('地图实例:', map ? '存在' : '不存在');
    console.log('数据点数量:', data.length);
    
    // 检查HeatMap插件是否可用（尝试多种可能的名称）
    let HeatMapClass = AMap.HeatMap || AMap.Heatmap;
    if (!HeatMapClass) {
      console.error('HeatMap插件未加载');
      return null;
    }
    console.log('HeatMap 插件已加载');
    
    // 计算数据的最大值用于归一化
    const maxWeight = data.length > 0 ? Math.max(...data.map(item => item[2] || 1)) : 100;
    console.log('最大权重值:', maxWeight);
    
    // 增强的颜色渐变方案 - 使用更鲜明的颜色，提高对比度
    const enhancedGradient = options.gradient || {
      0.0: 'rgba(0, 0, 255, 0.3)',      // 深蓝 - 低密度（带透明度）
      0.1: 'rgba(0, 100, 255, 0.5)',    // 浅蓝
      0.3: 'rgba(0, 200, 255, 0.7)',    // 青色
      0.5: 'rgba(0, 255, 100, 0.8)',    // 绿色
      0.7: 'rgba(255, 255, 0, 0.9)',    // 黄色
      0.85: 'rgba(255, 150, 0, 0.95)',  // 橙色
      1.0: 'rgba(255, 0, 0, 1.0)'       // 红色 - 高密度
    };
    
    const defaultHeatMapOptions = {
      radius: options.radius || 50,           // 默认半径增大到50
      opacity: options.opacity || 0.95,       // 默认透明度提高到0.95
      gradient: enhancedGradient,
      zIndex: options.zIndex || 999,          // 确保在最上层
      visible: options.visible !== false,
      // 新增配置选项
      maxOpacity: options.maxOpacity || 1.0,  // 最大透明度
      minOpacity: options.minOpacity || 0.4,  // 最小透明度提高
      blur: options.blur || 10                // 减小模糊度使边缘更清晰
    };
    
    console.log('热力图配置:', defaultHeatMapOptions);
    
    let heatMap;
    
    // 尝试使用标准方式创建热力图 - 直接将地图实例传递给构造函数
    try {
      console.log('正在创建 HeatMap 实例...');
      console.log('地图对象:', map);
      console.log('地图类型:', typeof map);
      
      // 高德地图 HeatMap 构造函数参数：new AMap.HeatMap(map, opts)
      heatMap = new HeatMapClass(map, {
        ...defaultHeatMapOptions,
        ...options
      });
      
      console.log('HeatMap 实例创建成功:', heatMap ? '是' : '否');
      console.log('HeatMap 类型:', typeof heatMap);
      console.log('HeatMap 方法:', Object.keys(heatMap || {}));
      
      // 检查是否正确关联到地图
      if (heatMap && typeof heatMap.getMap === 'function') {
        const attachedMap = heatMap.getMap();
        console.log('HeatMap 是否关联到地图:', attachedMap ? '是' : '否');
      }
    } catch (error) {
      console.error('创建热力图失败:', error);
      console.error('错误详情:', error.message);
      console.error('错误堆栈:', error.stack);
      return null;
    }
    
    // 如果有数据，尝试设置数据
    if (data.length > 0 && heatMap && typeof heatMap.setData === 'function') {
      try {
        console.log('正在设置热力图数据...');
        // 高德地图HeatMap.setData需要一个包含data属性的对象
        // 降低 max 值使颜色更容易达到红色（高密度）
        const maxDataValue = Math.max(5, Math.ceil(maxWeight * 0.5));
        console.log('数据最大值设置为:', maxDataValue, '实际最大权重:', maxWeight);
        
        heatMap.setData({
          data: data,
          max: maxDataValue
        });
        console.log('热力图数据设置成功');
        
        // 强制显示热力图
        if (typeof heatMap.show === 'function') {
          heatMap.show();
          console.log('热力图已强制显示');
        }
      } catch (error) {
        console.error('设置热力图数据失败:', error);
      }
    }
    
    console.log('=== createHeatMap 完成 ===');
    return heatMap;
  } catch (error) {
    console.error('创建热力图失败:', error);
    return null;
  }
}

/**
 * 创建云数据图层
 * @param {AMap} AMap - AMap命名空间
 * @param {Object} options - 云数据图层选项
 * @returns {AMap.CloudDataLayer} 云数据图层实例
 */
export function createCloudDataLayer(AMap, options = {}) {
  try {
    const defaultCloudOptions = {
      datasetId: options.datasetId || '',
      searchParams: options.searchParams || {},
      zIndex: options.zIndex || 10,
      visible: options.visible !== false
    };
    
    return new AMap.CloudDataLayer({
      ...defaultCloudOptions,
      ...options
    });
  } catch (error) {
    console.error('创建云数据图层失败:', error);
    return null;
  }
}
