/**
 * 知识库视图
 * 
 * 提供知识库浏览、搜索和模板管理功能
 */

import React, { useState, useMemo } from 'react';
import {
  Card,
  Input,
  Select,
  List,
  Typography,
  Tag,
  Space,
  Button,
  Tabs,
  Modal,
  message,
  Empty,
  Spin,
} from 'antd';
import type { TabsProps } from 'antd';
import {
  SearchOutlined,
  FileTextOutlined,
  BookOutlined,
  FolderOutlined,
  TagsOutlined,
  CopyOutlined,
} from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useKnowledgeSearchQuery, useKnowledgeItemsQuery, useTemplatesQuery, useTemplateQuery } from '../../services/knowledge';
import type { KnowledgeItem } from '../../services/knowledge';

const { Text } = Typography;
const { Search } = Input;
const { Option } = Select;

const KnowledgeView: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>(undefined);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [selectedItem, setSelectedItem] = useState<KnowledgeItem | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [activeTab, setActiveTab] = useState<'browse' | 'search' | 'templates'>('browse');

  // 搜索查询
  const { data: searchResults, isLoading: isSearching } = useKnowledgeSearchQuery(
    searchQuery,
    selectedCategory,
    selectedTags.length > 0 ? selectedTags : undefined
  );

  // 浏览知识库项
  const { data: items = [], isLoading: isLoadingItems } = useKnowledgeItemsQuery(selectedCategory);

  // 模板列表
  const { data: templates = [] } = useTemplatesQuery();

  // 过滤和排序知识库项
  const filteredItems = useMemo(() => {
    let result = items;
    
    // 按标签筛选
    if (selectedTags.length > 0) {
      result = result.filter(item => 
        selectedTags.some(tag => item.tags.includes(tag))
      );
    }
    
    // 按搜索关键词筛选
    if (searchQuery) {
      const queryLower = searchQuery.toLowerCase();
      result = result.filter(item =>
        item.title.toLowerCase().includes(queryLower) ||
        item.content.toLowerCase().includes(queryLower)
      );
    }
    
    // 按更新时间排序
    result.sort((a, b) => {
      const aTime = a.updated_at || a.created_at || '';
      const bTime = b.updated_at || b.created_at || '';
      return bTime.localeCompare(aTime);
    });
    
    return result;
  }, [items, selectedTags, searchQuery]);

  // 获取所有标签
  const allTags = useMemo(() => {
    const tagSet = new Set<string>();
    items.forEach(item => {
      item.tags.forEach(tag => tagSet.add(tag));
    });
    return Array.from(tagSet).sort();
  }, [items]);

  const handleItemClick = (item: KnowledgeItem) => {
    setSelectedItem(item);
    setShowDetailModal(true);
  };

  const handleCopyContent = (content: string) => {
    navigator.clipboard.writeText(content);
    message.success('内容已复制到剪贴板');
  };

  const getCategoryColor = (category: string) => {
    const colorMap: Record<string, string> = {
      rules: 'blue',
      playbooks: 'green',
      templates: 'orange',
      cases: 'purple',
    };
    return colorMap[category] || 'default';
  };

  const getCategoryIcon = (category: string) => {
    const iconMap: Record<string, React.ReactNode> = {
      rules: <FileTextOutlined />,
      playbooks: <BookOutlined />,
      templates: <FolderOutlined />,
      cases: <FileTextOutlined />,
    };
    return iconMap[category] || <FileTextOutlined />;
  };

  const tabItems: TabsProps['items'] = [
    {
      key: 'browse',
      label: '浏览',
      children: (
        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          {/* 筛选器 */}
          <Space wrap>
            <Select
              placeholder="选择类别"
              style={{ width: 150 }}
              allowClear
              value={selectedCategory}
              onChange={setSelectedCategory}
            >
              <Option value="rules">规则</Option>
              <Option value="playbooks">剧本</Option>
              <Option value="templates">模板</Option>
              <Option value="cases">案例</Option>
            </Select>
            <Select
              mode="multiple"
              placeholder="选择标签"
              style={{ width: 200 }}
              allowClear
              value={selectedTags}
              onChange={setSelectedTags}
            >
              {allTags.map(tag => (
                <Option key={tag} value={tag}>{tag}</Option>
              ))}
            </Select>
            <Search
              placeholder="搜索知识库..."
              allowClear
              style={{ width: 300 }}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onSearch={setSearchQuery}
            />
          </Space>

          {/* 知识库项列表 */}
          {isLoadingItems ? (
            <Spin tip="加载中..." />
          ) : filteredItems.length === 0 ? (
            <Empty description="暂无知识库项" />
          ) : (
            <List
              dataSource={filteredItems}
              renderItem={(item) => (
                <List.Item
                  style={{ cursor: 'pointer' }}
                  onClick={() => handleItemClick(item)}
                >
                  <List.Item.Meta
                    avatar={getCategoryIcon(item.category)}
                    title={
                      <Space>
                        <Text strong>{item.title}</Text>
                        <Tag color={getCategoryColor(item.category)}>
                          {item.category}
                        </Tag>
                      </Space>
                    }
                    description={
                      <Space direction="vertical" size="small" style={{ width: '100%' }}>
                        <Text type="secondary" ellipsis>
                          {item.content.substring(0, 200)}...
                        </Text>
                        <Space size="small">
                          {item.tags.map(tag => (
                            <Tag key={tag} icon={<TagsOutlined />}>
                              {tag}
                            </Tag>
                          ))}
                          {item.updated_at && (
                            <Text type="secondary" style={{ fontSize: '12px' }}>
                              更新于: {new Date(item.updated_at).toLocaleString('zh-CN')}
                            </Text>
                          )}
                        </Space>
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          )}
        </Space>
      ),
    },
    {
      key: 'search',
      label: '搜索',
      children: (
        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          <Search
            placeholder="输入搜索关键词..."
            allowClear
            size="large"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onSearch={setSearchQuery}
            enterButton={<SearchOutlined />}
          />

          {selectedCategory && (
            <Select
              placeholder="选择类别"
              style={{ width: 150 }}
              allowClear
              value={selectedCategory}
              onChange={setSelectedCategory}
            >
              <Option value="rules">规则</Option>
              <Option value="playbooks">剧本</Option>
              <Option value="templates">模板</Option>
              <Option value="cases">案例</Option>
            </Select>
          )}

          {isSearching ? (
            <Spin tip="搜索中..." />
          ) : searchQuery && searchResults ? (
            <>
              <Text type="secondary">
                找到 {searchResults.total} 个结果
              </Text>
              <List
                dataSource={searchResults.results}
                renderItem={(item) => (
                  <List.Item
                    style={{ cursor: 'pointer' }}
                    onClick={() => handleItemClick(item)}
                  >
                    <List.Item.Meta
                      avatar={getCategoryIcon(item.category)}
                      title={
                        <Space>
                          <Text strong>{item.title}</Text>
                          <Tag color={getCategoryColor(item.category)}>
                            {item.category}
                          </Tag>
                        </Space>
                      }
                      description={
                        <Text type="secondary" ellipsis>
                          {item.content.substring(0, 200)}...
                        </Text>
                      }
                    />
                  </List.Item>
                )}
              />
            </>
          ) : (
            <Empty description="请输入搜索关键词" />
          )}
        </Space>
      ),
    },
    {
      key: 'templates',
      label: '模板',
      children: <TemplatesList templates={templates} />,
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card
        title={
          <Space>
            <BookOutlined />
            <span>知识库</span>
          </Space>
        }
        style={{ marginBottom: 16 }}
      >
        <Tabs activeKey={activeTab} onChange={(key) => setActiveTab(key as any)} items={tabItems} />
      </Card>

      {/* 详情 Modal */}
      <Modal
        title={
          selectedItem ? (
            <Space>
              {getCategoryIcon(selectedItem.category)}
              <span>{selectedItem.title}</span>
              <Tag color={getCategoryColor(selectedItem.category)}>
                {selectedItem.category}
              </Tag>
            </Space>
          ) : null
        }
        open={showDetailModal}
        onCancel={() => setShowDetailModal(false)}
        footer={[
          <Button
            key="copy"
            icon={<CopyOutlined />}
            onClick={() => selectedItem && handleCopyContent(selectedItem.content)}
          >
            复制内容
          </Button>,
          <Button key="close" onClick={() => setShowDetailModal(false)}>
            关闭
          </Button>,
        ]}
        width={800}
      >
        {selectedItem && (
          <div style={{ maxHeight: '60vh', overflowY: 'auto' }}>
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              {selectedItem.tags.length > 0 && (
                <div>
                  <Text strong>标签: </Text>
                  {selectedItem.tags.map(tag => (
                    <Tag key={tag} icon={<TagsOutlined />}>
                      {tag}
                    </Tag>
                  ))}
                </div>
              )}
              {(selectedItem.created_at || selectedItem.updated_at) && (
                <div>
                  {selectedItem.created_at && (
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      创建于: {new Date(selectedItem.created_at).toLocaleString('zh-CN')}
                    </Text>
                  )}
                  {selectedItem.updated_at && (
                    <>
                      {' • '}
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        更新于: {new Date(selectedItem.updated_at).toLocaleString('zh-CN')}
                      </Text>
                    </>
                  )}
                </div>
              )}
              <div style={{ borderTop: '1px solid #f0f0f0', paddingTop: '16px' }}>
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {selectedItem.content}
                </ReactMarkdown>
              </div>
            </Space>
          </div>
        )}
      </Modal>
    </div>
  );
};

// 模板列表组件
const TemplatesList: React.FC<{ templates: string[] }> = ({ templates }) => {
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const { data: templateData } = useTemplateQuery(selectedTemplate || '');

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="middle">
      {templates.length === 0 ? (
        <Empty description="暂无模板" />
      ) : (
        <List
          dataSource={templates}
          renderItem={(template) => (
            <List.Item
              style={{ cursor: 'pointer' }}
              onClick={() => setSelectedTemplate(template)}
            >
              <List.Item.Meta
                avatar={<FolderOutlined />}
                title={<Text strong>{template}</Text>}
              />
            </List.Item>
          )}
        />
      )}

      {selectedTemplate && templateData && (
        <Card
          title={`模板: ${selectedTemplate}`}
          extra={
            <Button
              icon={<CopyOutlined />}
              onClick={() => {
                navigator.clipboard.writeText(templateData.content);
                message.success('模板内容已复制');
              }}
            >
              复制模板
            </Button>
          }
        >
          <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {templateData.content}
            </ReactMarkdown>
          </div>
        </Card>
      )}
    </Space>
  );
};

export default KnowledgeView;
