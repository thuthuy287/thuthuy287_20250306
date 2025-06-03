# 
# ANSA Version
#
    ANSA_Version = 19.1.3
# 
# Mesh parameters
#
    mesh_parameters_name      = 3mm_Param_VINFAST
    mesh_parameters_delimiter = ||
# 
# Shell Mesh
#
# 
# General Mesh
#
    mesh_type               = general
    element_type            = mixed
    element_order           = first
    existing_mesh_treatment = erase
    target_element_length   = 3
    general_min_target_len  = 1.01
    general_max_target_len  = 5.99
# 
# CFD
# 
    cfd_interior_growth_rate             = 1.2
    cfd_distortion_angle                 = 20.
    cfd_min_length                       = 1.
    cfd_max_length                       = 100.
    cfd_auto_length_calculation          = false
    cfd_enhanced_curvature_sampling_flag = false
    cfd_sharpen_edges_angle_limit        = 30.
    cfd_convex_sharp_edges_length_flag   = false
    cfd_convex_sharp_edges_length        = 10.
    cfd_convex_sharp_edges_length_mode   = absolute
    cfd_concave_sharp_edges_length_flag  = false
    cfd_concave_sharp_edges_length       = 10.
    cfd_concave_sharp_edges_length_mode  = absolute
    cfd_refine_trailing_edges_ratio_flag = false
    cfd_refine_trailing_edges_ratio      = 1.
    cfd_refine_trailing_edges_angle      = 60.
    cfd_free_edges_length_flag           = false
    cfd_free_edges_length                = 10.
    cfd_free_edges_length_mode           = absolute
    cfd_pid_proximity                    = false
    cfd_proximity_based_on               = whole_model
    cfd_self_proximity                   = false
    cfd_max_angle_between_normals        = 40.
    cfd_length_to_gap_refinement_factor  = 0.3
    cfd_convex_curvature_treatment       = false
    cfd_reduce_max_length                = true
    cfd_reduce_local_length              = false
    cfd_orientation_based_refinement     = false
    cfd_reduction_factor                 = 0.5
    cfd_max_radius_of_curvature          = 1000.
    cfd_orientation_vector_dx            = 0.
    cfd_orientation_vector_dy            = 0.
    cfd_orientation_vector_dz            = -1.
    cfd_max_angle_deviation              = 60.
# 
# STL
# 
    stl_distortion_distance     = 0.2
    stl_max_length              = 0.
    stl_min_length              = 0.05
    stl_distortion_angle_value  = 20.
    stl_distortion_angle_flag   = false
# 
# Feature options
# 
    bm_features_handling   = Recognize features
    orientation_handling   = use_existing
    orientation_definition = grey outside volume
# 
# Freeze
# 
    freeze_single_bounds = true
    freeze_triple_bounds = false
    freeze_perimeters    = false
    freeze_line_elements = false
    freeze_named_grids   = false
    freeze_holes         = false
# 
# Remove triangles from
# 
    remove_triangle_from_spots     = true
    remove_triangle_from_int_perim = true
    remove_triangle_from_ext_perim = true
# 
# Zones options
# 
    attach_zones_on_perimeters              = 0.5
    create_perims_on_zones                  = false
    create_ortho_trias_on_zones             = false
    create_zones_only_on_flat_areas         = true
    create_corner_quads_at_zones            = false
# 
# Flanges 3D options
# 
    flanges_3d_refine_perimeters = true
# 
# Fillets options
# 
    create_mapped_mesh_in_fillets   = true
# 
# Holes 3D options
# 
    create_ortho_trias_on_holes_3d = true
# 
# Perimeters
#
    cfd_fix_violating_shells_by_smoothing_over_perimeters = false
    defeaturing_length                                    = 0.5
    paste_triple_bounds_distance                          = 0.5
    flat_perimeters_defeaturing_level                     = fine
    maintain_sharp_edge_ribs                              = false
    maintain_set_or_include_bounds                        = true
    set_perimeters_treatment                              = forbid_join
    dont_release_already_joined_perims                    = false
    create_perims_on_symmetry_plane                       = false
    cut_mesh_on_symmetry_plane                            = false
    freeze_segments_in_symmetry                           = true
    recognize_property_bounds_as_perimeters               = true
    recognize_part_bounds_as_perimeters                   = true
    recognize_feature_line_bounds_as_perimeters           = true
    recognize_feature_line_bounds_option                  = Angle
    recognize_feature_line_bounds_angle                   = 5.
    recognize_feature_line_bounds_corner_angle            = 15.
    user_defined_feature_lines                            = true
    recognize_feature_line_auto_close                     = true
    treat_perimeters                                      = false
    rule_perimeter                                        = default = false || active = true || sides = none || angle = none || pid = - || part = - || sets_names = none || treatment = 1
    rule_perimeter                                        = default = false || active = true || sides = none || angle = none || pid = - || part = - || sets_names = none || treatment = 1
    rule_perimeter                                        = default = true || active = false || sides = none || angle = none || pid = - || part = - || sets_names = none || treatment = 2
    treatment_perimeter                                   = 1 || name = none || join = true || join_option = forbid || spacing = false || spacing_option = auto || number_or_length = 0 || zones = false || zones_option = off || specific_zones = none || radial_offset = false || blended = false || smooth_zones = full || proximity_distance_factor = 0. || proximity_distance_option = * last height || cut_faces_on_zones = false || first_height_option = Absolute first height || first_height_value = 0.1 || growth_factor = 1.2 || zones_number = 5 || max_aspect = 0.4 || separate_angle = 90. || connect_angle = 60. || element_type = quad
    treatment_perimeter                                   = 2 || name = none || join = false || join_option = auto || spacing = true || spacing_option = auto || number_or_length = 0 || zones = false || zones_option = off || specific_zones = none || radial_offset = false || blended = false || smooth_zones = full || proximity_distance_factor = 0. || proximity_distance_option = * last height || cut_faces_on_zones = false || first_height_option = Absolute first height || first_height_value = 0.1 || growth_factor = 1.2 || zones_number = 5 || max_aspect = 0.4 || separate_angle = 90. || connect_angle = 60. || element_type = quad
# 
# Fillets
# 
    recognize_fillets                   = true
    recognize_fillets_max_radius        = 30.
    recognize_fillets_min_angle         = 5.
    treat_fillets                       = true
    rule_fillet                         = default = false || active = true || convexity = none || radius = none || width = 0-3 || angle = none || treatment = 15
    rule_fillet                         = default = false || active = true || convexity = none || radius = none || width = 3-5.5 || angle = none || treatment = 16
    rule_fillet                         = default = false || active = true || convexity = none || radius = none || width = 5.5-8.5 || angle = none || treatment = 17
    rule_fillet                         = default = true || active = true || convexity = none || radius = none || width = none || angle = none || treatment = 18
    treatment_fillet                    = 15 || name = none || defeaturing = false || defeaturing_option = off || forbid_join_perimeters_created_from_split = false || join_upper_lower_perimeters_during_split = false || length = false || length_value = none || rows = true || rows_option = specific || custom_distortion = false || distortion_distance = 20% || distortion_angle = 0. || even_rows = false || rows_number = 1
    treatment_fillet                    = 16 || name = none || defeaturing = false || defeaturing_option = split || forbid_join_perimeters_created_from_split = false || join_upper_lower_perimeters_during_split = true || length = false || length_value = none || rows = true || rows_option = specific || custom_distortion = false || distortion_distance = 20% || distortion_angle = 0. || even_rows = false || rows_number = 2
    treatment_fillet                    = 17 || name = none || defeaturing = false || defeaturing_option = split || forbid_join_perimeters_created_from_split = false || join_upper_lower_perimeters_during_split = true || length = false || length_value = none || rows = true || rows_option = specific || custom_distortion = false || distortion_distance = 20% || distortion_angle = 0. || even_rows = false || rows_number = 3
    treatment_fillet                    = 18 || name = none || defeaturing = false || defeaturing_option = split || forbid_join_perimeters_created_from_split = false || join_upper_lower_perimeters_during_split = true || length = false || length_value = none || rows = true || rows_option = auto || custom_distortion = false || distortion_distance = 20% || distortion_angle = 0. || even_rows = false || rows_number = 0
# 
# Chamfers
# 
    recognize_chamfers           = false
    recognize_chamfers_min_angle = 20.
    recognize_chamfers_max_angle = 70.
    recognize_chamfers_max_width = 1.
    treat_chamfers               = false
    rule_chamfer                 = default = true || active = true || width = none || angle = none || treatment = 19
    treatment_chamfer            = 19 || name = none || defeaturing = true || defeaturing_option = off
# 
# Flanges 2D
#
    recognize_flanges_2d                      = true
    recognize_flanges_2d_proximity            = true
    recognize_flanges_2d_proximity_option     = factor
    recognize_flanges_2d_proximity_factor     = 1.2
    recognize_flanges_2d_proximity_distance   = 2.5
    recognize_flanges_2d_proximity_angle      = 10.
    recognize_flanges_2d_min_width            = 0.
    recognize_flanges_2d_max_width            = 50.
    recognize_flanges_2d_connections          = false
    recognize_flanges_2d_connections_option   = Specified distance
    recognize_flanges_2d_connections_distance = 2.5
    treat_flanges_2d                          = true
    rule_flange_2d                            = default = false || active = true || width = <3 || proximity = >=50 || connections = - || treatment = 20
    rule_flange_2d                            = default = false || active = true || width = 3-5.5 || proximity = >=50 || connections = - || treatment = 21
    rule_flange_2d                            = default = false || active = true || width = >5.5 || proximity = >=50 || connections = - || treatment = 22
    rule_flange_2d                            = default = true || active = false || width = none || proximity = none || connections = - || treatment = 23
    treatment_flange_2d                       = 20 || name = none || length = false || length_value = none || rows = true || rows_option = number || rows_number = 1
    treatment_flange_2d                       = 21 || name = none || length = false || length_value = none || rows = true || rows_option = number || rows_number = 2
    treatment_flange_2d                       = 22 || name = none || length = false || length_value = none || rows = true || rows_option = number || rows_number = 3
    treatment_flange_2d                       = 23 || name = none || length = true || length_value = 0.5*L || rows = false || rows_option = number || rows_number = none
# 
# Flanges 3D
# 
    recognize_flanges_3d                    = true
    recognize_flanges_3d_proximity          = false
    recognize_flanges_3d_proximity_distance = 0.5
    recognize_flanges_3d_proximity_angle    = 5.
    treat_flanges_3d                        = false
    rule_flange_3d                          = default = true || active = true || area = none || proximity = none || treatment = 29
    treatment_flange_3d                     = 29 || name = none || length = true || length_value = 0.5*L
# 
# Holes 2D
#
    recognize_holes_2d                     = false
    recognize_holes_2d_external_perimeters = true
    recognize_holes_2d_proximity           = false
    recognize_holes_2d_proximity_distance  = 10.
    recognize_holes_2d_proximity_angle     = 10.
    recognize_holes_2d_connections         = true
    recognize_holes_2d_connections_option  = bolt
    treat_holes_2d                         = false
    rule_hole_2d                           = default = false || active = true || shape = Round || diam_or_size = <9.8 || size_2 = none || ratio = none || eq_diameter = none || proximity = - || connection = - || treatment = 3
    rule_hole_2d                           = default = false || active = true || shape = Oval || diam_or_size = <5.01 || size_2 = none || ratio = none || eq_diameter = none || proximity = - || connection = - || treatment = 4
    rule_hole_2d                           = default = false || active = true || shape = Rectangular|Concyclic || diam_or_size = <4.01 || size_2 = none || ratio = none || eq_diameter = none || proximity = - || connection = - || treatment = 5
    rule_hole_2d                           = default = false || active = true || shape = none || diam_or_size = 7.5-11 || size_2 = none || ratio = none || eq_diameter = none || proximity = - || connection = - || treatment = 6
    rule_hole_2d                           = default = false || active = true || shape = none || diam_or_size = 7.5-11 || size_2 = none || ratio = none || eq_diameter = none || proximity = - || connection = true || treatment = 7
    rule_hole_2d                           = default = false || active = true || shape = none || diam_or_size = 11-13 || size_2 = none || ratio = none || eq_diameter = none || proximity = - || connection = - || treatment = 8
    rule_hole_2d                           = default = false || active = true || shape = none || diam_or_size = 11-13 || size_2 = none || ratio = none || eq_diameter = none || proximity = - || connection = true || treatment = 9
    rule_hole_2d                           = default = false || active = true || shape = none || diam_or_size = 13-15 || size_2 = none || ratio = none || eq_diameter = none || proximity = - || connection = - || treatment = 10
    rule_hole_2d                           = default = false || active = true || shape = none || diam_or_size = 13-15 || size_2 = none || ratio = none || eq_diameter = none || proximity = - || connection = true || treatment = 11
    rule_hole_2d                           = default = false || active = true || shape = none || diam_or_size = 15.-32. || size_2 = none || ratio = none || eq_diameter = none || proximity = - || connection = - || treatment = 12
    rule_hole_2d                           = default = false || active = true || shape = none || diam_or_size = 15.-32. || size_2 = none || ratio = none || eq_diameter = none || proximity = - || connection = true || treatment = 13
    rule_hole_2d                           = default = true || active = true || shape = none || diam_or_size = none || size_2 = none || ratio = none || eq_diameter = none || proximity = - || connection = - || treatment = 14
    treatment_hole_2d                      = 3 || name = none || defeaturing = true || defeaturing_option = fill || nodes_number = false || number_value = auto || treat_as_round = false || zones = false || zones_option = off || specific_zones = none || target_diam_or_size = false || target_diam_or_size_value = none
    treatment_hole_2d                      = 4 || name = none || defeaturing = true || defeaturing_option = fill || nodes_number = false || number_value = auto || treat_as_round = false || zones = false || zones_option = specific || specific_zones = none || target_diam_or_size = false || target_diam_or_size_value = none
    treatment_hole_2d                      = 5 || name = none || defeaturing = true || defeaturing_option = fill || nodes_number = false || number_value = auto || treat_as_round = false || zones = false || zones_option = specific || specific_zones = none || target_diam_or_size = false || target_diam_or_size_value = none
    treatment_hole_2d                      = 6 || name = none || defeaturing = false || defeaturing_option = fill || nodes_number = true || number_value = 4 || treat_as_round = true || zones = false || zones_option = specific || specific_zones = none || target_diam_or_size = true || target_diam_or_size_value = D
    treatment_hole_2d                      = 7 || name = none || defeaturing = false || defeaturing_option = fill || nodes_number = true || number_value = 4 || treat_as_round = true || zones = true || zones_option = specific || specific_zones = width = D/2 || target_diam_or_size = true || target_diam_or_size_value = D
    treatment_hole_2d                      = 8 || name = none || defeaturing = false || defeaturing_option = off || nodes_number = true || number_value = 6 || treat_as_round = true || zones = false || zones_option = specific || specific_zones = width = W=D/2 || target_diam_or_size = true || target_diam_or_size_value = D
    treatment_hole_2d                      = 9 || name = none || defeaturing = false || defeaturing_option = fill || nodes_number = true || number_value = 6 || treat_as_round = true || zones = true || zones_option = specific || specific_zones = width = D/2 || target_diam_or_size = true || target_diam_or_size_value = D
    treatment_hole_2d                      = 10 || name = none || defeaturing = false || defeaturing_option = off || nodes_number = true || number_value = 8 || treat_as_round = true || zones = false || zones_option = specific || specific_zones = width = W=D/2 || target_diam_or_size = true || target_diam_or_size_value = D
    treatment_hole_2d                      = 11 || name = none || defeaturing = false || defeaturing_option = fill || nodes_number = true || number_value = 8 || treat_as_round = true || zones = true || zones_option = specific || specific_zones = width = D/2 || target_diam_or_size = true || target_diam_or_size_value = D
    treatment_hole_2d                      = 12 || name = none || defeaturing = false || defeaturing_option = off || nodes_number = true || number_value = auto || treat_as_round = true || zones = false || zones_option = specific || specific_zones = width = W=D/4,width = W=D/4 || target_diam_or_size = true || target_diam_or_size_value = D
    treatment_hole_2d                      = 13 || name = none || defeaturing = false || defeaturing_option = off || nodes_number = true || number_value = auto || treat_as_round = true || zones = false || zones_option = specific || specific_zones = width = W=D/4,width = W=D/4 || target_diam_or_size = true || target_diam_or_size_value = D
    treatment_hole_2d                      = 14 || name = none || defeaturing = false || defeaturing_option = off || nodes_number = true || number_value = auto || treat_as_round = true || zones = false || zones_option = off || specific_zones = none || target_diam_or_size = true || target_diam_or_size_value = D
# 
# Holes 3D
# 
    recognize_holes_3d                    = false
    recognize_holes_3d_connections        = false
    recognize_holes_3d_connections_option = bolt
    treat_holes_3d                        = false
    rule_hole_3d                          = default = true || active = true || diameter = none || height = none || straight = - || blind = - || connection = - || treatment = 28
    treatment_hole_3d                     = 28 || defeaturing = false || defeaturing_option = off || nodes_number = true || number_value = auto || zones = false || zones_option = off || specific_zones = none
# 
# Logos
#
    recognize_logos        = false
    recognize_logos_height = 0.
    recognize_logos_size   = 0.
    treat_logos            = false
    rule_logo              = default = true || active = true || height = none || size = none || treatment = 27
    treatment_logo         = 27 || name = none || defeaturing = true || defeaturing_option = remove
# 
# Stamps
#
    recognize_stamps        = false
    recognize_stamps_height = 10.
    recognize_stamps_size   = 15.
    treat_stamps            = false
    rule_stamp              = default = false || active = true || height = <3 || size = none || treatment = 24
    rule_stamp              = default = false || active = true || height = 3-10 || size = 10-15 || treatment = 25
    rule_stamp              = default = false || active = true || height = 3-10 || size = >15 || treatment = 26
    rule_stamp              = default = true || active = true || height = none || size = none || treatment = 24
    treatment_stamp         = 24 || name = none || defeaturing = true || defeaturing_option = remove
    treatment_stamp         = 25 || name = none || defeaturing = true || defeaturing_option = auto
    treatment_stamp         = 26 || name = none || defeaturing = true || defeaturing_option = auto
# 
# Ribs
#
    recognize_ribs_2d = true
# 
# Fix Quality
#
    fix_elements_general_flag           = true
    split_remain_viol_quads_flag        = false
    fix_minimum_length_in_fillets       = true
    fix_minimum_length_in_flanges_2d    = true
    allow_hole_2d_zones_deformation     = false
    create_perfect_hole_2d_zone         = false
    zones_around_violating              = 2
    maximum_distance_from_surface       = 0.01
    maximum_distance_from_perimeter     = 0.5
    maximum_distance_from_triple_bounds = 0.5
# 
# Volume Mesh
#
# 
# Volume Fix Quality
# 
    fix_solid_elements_general_flag       = false
    freeze_non_visible_shells             = false
    unconstrained_2nd_order_nodes         = false
    fix_solid_freeze_line_elements        = true
    number_of_affected_solid_zones        = 3
    fix_volume_external_bounds            = constrained
    maximum_distance_from_external_bounds = 0.1*local
    fix_volume_pid_bounds                 = unconstrained
    maximum_distance_from_pid_bounds      = 0.1*local
# 
# CONS Resolution
# 
    perimeter_length                   = 3.
    distortion-distance                = 20.%
    distortion-angle                   = 45.
# 
# Unstructured Volume Mesh Options
# 
    create_volume_mesh            = false
    tetras_algorithm              = Tetra Rapid
    tetras_criterion_type         = NASTRAN_Aspect_Ratio
    tetras_criterion_value        = 4.
    tetras_max_growth_rate        = 1.2
    refine_shell_mesh_proximities = false
    tetras_max_elem_length        = 0.
    hexa_coordinate_system        = 0
    hexa_buffer_zones             = 3
    create_pyramids               = true
    force2rows                    = false
    frozen_entities_set_id        = 0
    trans_pnt_offs                = true
    do_not_violate_max_len        = false
    light_volume_representation   = false
