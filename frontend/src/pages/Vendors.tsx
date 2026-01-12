import { useState, useRef, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Search, MoreVertical, Building2, Loader2, Pencil, Trash2 } from 'lucide-react';
import {
  Button,
  Input,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Badge,
  Label,
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui';
import apiClient, { getApiErrorMessage } from '@/lib/api';
import type { Vendor, VendorTier, VendorStatus, CreateVendorRequest, UpdateVendorRequest } from '@/types/api';

export function Vendors() {
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedVendor, setSelectedVendor] = useState<Vendor | null>(null);
  const [openMenuId, setOpenMenuId] = useState<string | null>(null);
  const [createError, setCreateError] = useState<string | null>(null);
  const [editError, setEditError] = useState<string | null>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  // Form state for new vendor
  const [newVendor, setNewVendor] = useState<CreateVendorRequest>({
    name: '',
    website: '',
    description: '',
    tier: 'medium',
    tags: [],
  });

  // Form state for editing vendor
  const [editVendor, setEditVendor] = useState<UpdateVendorRequest>({
    name: '',
    website: '',
    description: '',
    tier: 'medium',
    status: 'active',
  });

  // Close menu when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setOpenMenuId(null);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const { data: vendorsResponse, isLoading } = useQuery({
    queryKey: ['vendors', searchQuery],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (searchQuery) params.append('search', searchQuery);
      params.append('limit', '50');

      const response = await apiClient.get(`/vendors?${params}`);
      return response.data;
    },
  });

  const createVendorMutation = useMutation({
    mutationFn: async (vendor: CreateVendorRequest) => {
      const response = await apiClient.post('/vendors', vendor);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vendors'] });
      setShowCreateModal(false);
      setNewVendor({ name: '', website: '', description: '', tier: 'medium', tags: [] });
      setCreateError(null);
    },
    onError: (error) => {
      setCreateError(getApiErrorMessage(error));
    },
  });

  const updateVendorMutation = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: UpdateVendorRequest }) => {
      const response = await apiClient.patch(`/vendors/${id}`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vendors'] });
      setShowEditModal(false);
      setSelectedVendor(null);
      setEditError(null);
    },
    onError: (error) => {
      setEditError(getApiErrorMessage(error));
    },
  });

  const deleteVendorMutation = useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/vendors/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vendors'] });
      setShowDeleteModal(false);
      setSelectedVendor(null);
    },
  });

  const handleCreateVendor = () => {
    if (!newVendor.name.trim()) {
      setCreateError('Vendor name is required');
      return;
    }
    setCreateError(null);
    createVendorMutation.mutate(newVendor);
  };

  const handleEditVendor = () => {
    if (!editVendor.name?.trim()) {
      setEditError('Vendor name is required');
      return;
    }
    if (!selectedVendor) return;
    setEditError(null);
    updateVendorMutation.mutate({ id: selectedVendor.id, data: editVendor });
  };

  const handleDeleteVendor = () => {
    if (!selectedVendor) return;
    deleteVendorMutation.mutate(selectedVendor.id);
  };

  const openEditModal = (vendor: Vendor) => {
    setSelectedVendor(vendor);
    setEditVendor({
      name: vendor.name,
      website: vendor.website || '',
      description: vendor.description || '',
      tier: vendor.tier,
      status: vendor.status,
    });
    setEditError(null);
    setShowEditModal(true);
    setOpenMenuId(null);
  };

  const openDeleteModal = (vendor: Vendor) => {
    setSelectedVendor(vendor);
    setShowDeleteModal(true);
    setOpenMenuId(null);
  };

  const vendors: Vendor[] = vendorsResponse?.data || [];

  const getTierVariant = (tier: VendorTier) => {
    switch (tier) {
      case 'critical':
        return 'critical';
      case 'high':
        return 'high';
      case 'medium':
        return 'medium';
      case 'low':
        return 'low';
      default:
        return 'secondary';
    }
  };

  const getStatusColor = (status: VendorStatus) => {
    switch (status) {
      case 'active':
        return 'text-green-600 bg-green-100';
      case 'inactive':
        return 'text-gray-600 bg-gray-100';
      case 'onboarding':
        return 'text-blue-600 bg-blue-100';
      case 'offboarding':
        return 'text-orange-600 bg-orange-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">Vendors</h1>
          <p className="text-muted-foreground">Manage your third-party vendors</p>
        </div>
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Add Vendor
        </Button>
      </div>

      {/* Create Vendor Modal */}
      <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Add New Vendor</DialogTitle>
            <DialogDescription>
              Add a third-party vendor to track their security posture.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="name">Vendor Name *</Label>
              <Input
                id="name"
                placeholder="e.g., Acme Corp"
                value={newVendor.name}
                onChange={(e) => setNewVendor({ ...newVendor, name: e.target.value })}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="website">Website</Label>
              <Input
                id="website"
                placeholder="https://example.com"
                value={newVendor.website || ''}
                onChange={(e) => setNewVendor({ ...newVendor, website: e.target.value })}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="description">Description</Label>
              <Input
                id="description"
                placeholder="Brief description of the vendor"
                value={newVendor.description || ''}
                onChange={(e) => setNewVendor({ ...newVendor, description: e.target.value })}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="tier">Risk Tier</Label>
              <select
                id="tier"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                value={newVendor.tier}
                onChange={(e) => setNewVendor({ ...newVendor, tier: e.target.value as VendorTier })}
              >
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
            {createError && (
              <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
                {createError}
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCreateModal(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreateVendor} disabled={createVendorMutation.isPending}>
              {createVendorMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Create Vendor
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Vendor Modal */}
      <Dialog open={showEditModal} onOpenChange={setShowEditModal}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Edit Vendor</DialogTitle>
            <DialogDescription>
              Update vendor information and risk classification.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="edit-name">Vendor Name *</Label>
              <Input
                id="edit-name"
                placeholder="e.g., Acme Corp"
                value={editVendor.name || ''}
                onChange={(e) => setEditVendor({ ...editVendor, name: e.target.value })}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="edit-website">Website</Label>
              <Input
                id="edit-website"
                placeholder="https://example.com"
                value={editVendor.website || ''}
                onChange={(e) => setEditVendor({ ...editVendor, website: e.target.value })}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="edit-description">Description</Label>
              <Input
                id="edit-description"
                placeholder="Brief description of the vendor"
                value={editVendor.description || ''}
                onChange={(e) => setEditVendor({ ...editVendor, description: e.target.value })}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="edit-tier">Risk Tier</Label>
              <select
                id="edit-tier"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                value={editVendor.tier || 'medium'}
                onChange={(e) => setEditVendor({ ...editVendor, tier: e.target.value as VendorTier })}
              >
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="edit-status">Status</Label>
              <select
                id="edit-status"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                value={editVendor.status || 'active'}
                onChange={(e) => setEditVendor({ ...editVendor, status: e.target.value as VendorStatus })}
              >
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="onboarding">Onboarding</option>
                <option value="offboarding">Offboarding</option>
              </select>
            </div>
            {editError && (
              <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
                {editError}
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowEditModal(false)}>
              Cancel
            </Button>
            <Button onClick={handleEditVendor} disabled={updateVendorMutation.isPending}>
              {updateVendorMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Modal */}
      <Dialog open={showDeleteModal} onOpenChange={setShowDeleteModal}>
        <DialogContent className="sm:max-w-[400px]">
          <DialogHeader>
            <DialogTitle>Delete Vendor</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete <strong>{selectedVendor?.name}</strong>? This action cannot be undone and will remove all associated documents and analysis data.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDeleteModal(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDeleteVendor} disabled={deleteVendorMutation.isPending}>
              {deleteVendorMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Delete Vendor
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Search and Filters */}
      <div className="flex gap-4 mb-6">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search vendors..."
            className="pl-9"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* Vendors Grid */}
      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-6 bg-muted rounded w-3/4"></div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="h-4 bg-muted rounded w-1/2"></div>
                  <div className="h-4 bg-muted rounded w-1/4"></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : vendors.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Building2 className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium mb-2">No vendors yet</h3>
            <p className="text-muted-foreground text-center mb-4">
              Add your first vendor to start tracking their security posture.
            </p>
            <Button onClick={() => setShowCreateModal(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Add Vendor
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {vendors.map((vendor) => (
            <Card key={vendor.id} className="hover:shadow-md transition-shadow">
              <CardHeader className="flex flex-row items-start justify-between space-y-0">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
                    <Building2 className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{vendor.name}</CardTitle>
                    {vendor.website && (
                      <a
                        href={vendor.website}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-muted-foreground hover:text-primary"
                        onClick={(e) => e.stopPropagation()}
                      >
                        {vendor.website.replace(/^https?:\/\//, '')}
                      </a>
                    )}
                  </div>
                </div>
                <div className="relative" ref={openMenuId === vendor.id ? menuRef : null}>
                  <button
                    className="rounded-full p-2 hover:bg-accent"
                    onClick={(e) => {
                      e.stopPropagation();
                      setOpenMenuId(openMenuId === vendor.id ? null : vendor.id);
                    }}
                  >
                    <MoreVertical className="h-4 w-4" />
                  </button>
                  {openMenuId === vendor.id && (
                    <div className="absolute right-0 top-full mt-1 w-36 rounded-md border bg-popover shadow-md z-50">
                      <button
                        className="flex w-full items-center gap-2 px-3 py-2 text-sm hover:bg-accent"
                        onClick={(e) => {
                          e.stopPropagation();
                          openEditModal(vendor);
                        }}
                      >
                        <Pencil className="h-4 w-4" />
                        Edit
                      </button>
                      <button
                        className="flex w-full items-center gap-2 px-3 py-2 text-sm text-destructive hover:bg-accent"
                        onClick={(e) => {
                          e.stopPropagation();
                          openDeleteModal(vendor);
                        }}
                      >
                        <Trash2 className="h-4 w-4" />
                        Delete
                      </button>
                    </div>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2 mb-3">
                  <Badge variant={getTierVariant(vendor.tier)}>{vendor.tier}</Badge>
                  <span className={`text-xs px-2 py-1 rounded-full capitalize ${getStatusColor(vendor.status)}`}>
                    {vendor.status}
                  </span>
                </div>
                {vendor.description && (
                  <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
                    {vendor.description}
                  </p>
                )}
                <div className="flex items-center justify-between text-sm text-muted-foreground">
                  <span>Last assessed: {vendor.lastAssessed ? new Date(vendor.lastAssessed).toLocaleDateString() : 'Never'}</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
