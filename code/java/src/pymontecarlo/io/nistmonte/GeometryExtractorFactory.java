package pymontecarlo.io.nistmonte;

import gov.nist.microanalysis.EPQLibrary.EPQException;
import gov.nist.microanalysis.EPQLibrary.ElectronRange;
import gov.nist.microanalysis.NISTMonte.IMaterialScatterModel;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS.Region;
import gov.nist.microanalysis.NISTMonte.MultiPlaneShape;
import gov.nist.microanalysis.Utility.Math2;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;

import org.jdom.Element;

import ptpshared.jdom.JDomUtils;

/**
 * Factory of geometry extractors.
 * 
 * @author ppinard
 */
public class GeometryExtractorFactory implements
        ExtractorFactory<GeometryExtractor> {

    /** Substrate extractor. */
    public static final GeometryExtractor SUBSTRATE =
            new AbstractGeometryExtractor(
                    "pymontecarlo.input.base.geometry.Substrate") {

                @Override
                public double[] extract(Element geometryImplElement,
                        Region chamber, double beamEnergy) throws IOException,
                        EPQException {
                    Map<Integer, IMaterialScatterModel> materials =
                            extractMaterials(geometryImplElement);
                    Map<Integer, Body> bodies =
                            extractBodies(geometryImplElement, materials);

                    int substrate =
                            JDomUtils.getIntegerFromAttribute(
                                    geometryImplElement, "substrate");
                    IMaterialScatterModel material =
                            bodies.get(substrate).material;

                    double[] normal = Math2.Z_AXIS;
                    double[] pt = Math2.ORIGIN_3D;
                    MultiPlaneShape shape =
                            MultiPlaneShape.createSubstrate(normal, pt);

                    new Region(chamber, material, shape); // add shape to
                                                          // chamber

                    return extractAndApplyRotationTilt(geometryImplElement,
                            chamber);
                }

            };

    /** Multi-layers extractor. */
    public static final GeometryExtractor MULTI_LAYERS =
            new AbstractGeometryExtractor(
                    "pymontecarlo.input.base.geometry.MultiLayers") {

                @Override
                public double[] extract(Element geometryImplElement,
                        Region chamber, double beamEnergy) throws IOException,
                        EPQException {
                    Map<Integer, IMaterialScatterModel> materials =
                            extractMaterials(geometryImplElement);
                    Map<Integer, Body> bodies =
                            extractBodies(geometryImplElement, materials);

                    // Layers
                    String[] tmpLayers =
                            JDomUtils.getStringFromAttribute(
                                    geometryImplElement, "layers").split(",");

                    MultiPlaneShape shape;
                    double[] normal = Math2.Z_AXIS;
                    double[] point = Math2.ORIGIN_3D;

                    Layer layer;
                    IMaterialScatterModel material;
                    double thickness;
                    for (String tmpLayer : tmpLayers) {
                        layer = (Layer) bodies.get(Integer.parseInt(tmpLayer));
                        thickness = layer.thickness;
                        material = layer.material;

                        shape =
                                MultiPlaneShape.createFilm(normal, point,
                                        thickness);
                        new Region(chamber, material, shape); // add shape to
                                                              // chamber

                        // Calculate next point
                        point =
                                Math2.minus(point,
                                        Math2.multiply(thickness, Math2.Z_AXIS));
                    }

                    int substrate =
                            JDomUtils.getIntegerFromAttribute(
                                    geometryImplElement, "substrate", -1);
                    if (substrate > 0) {
                        material = bodies.get(substrate).material;

                        double sc =
                                ElectronRange.KanayaAndOkayama1972.compute(
                                        material.getMaterial(), beamEnergy)
                                        / material.getMaterial().getDensity();
                        double dim = Math.max(10.0 * sc, 1.0e-4);
                        double[] dims = new double[] { dim, dim, dim };
                        point =
                                Math2.minus(point,
                                        Math2.multiply(dim / 2.0, Math2.Z_AXIS));
                        shape =
                                MultiPlaneShape.createBlock(dims, point, 0, 0,
                                        0);

                        new Region(chamber, material, shape); // add shape to
                                                              // chamber
                    }

                    return extractAndApplyRotationTilt(geometryImplElement,
                            chamber);
                }

            };

    /** Grain boundaries extractor. */
    public static final GeometryExtractor GRAIN_BOUNDARIES =
            new AbstractGeometryExtractor(
                    "pymontecarlo.input.base.geometry.GrainBoundaries") {

                @Override
                public double[] extract(Element geometryImplElement,
                        Region chamber, double beamEnergy) throws IOException,
                        EPQException {
                    Map<Integer, IMaterialScatterModel> materials =
                            extractMaterials(geometryImplElement);
                    Map<Integer, Body> bodies =
                            extractBodies(geometryImplElement, materials);

                    // Setup layers
                    List<Layer> layers = new ArrayList<Layer>();
                    double totalThickness = 0.0;

                    int leftSubstrate =
                            JDomUtils.getIntegerFromAttribute(
                                    geometryImplElement, "left_substrate");
                    layers.add(new Layer(bodies.get(leftSubstrate).material,
                            0.1));
                    totalThickness += 0.1;

                    String[] indexStrs =
                            JDomUtils.getStringFromAttribute(
                                    geometryImplElement, "layers").split(",");
                    Layer tmpLayer;
                    for (String indexStr : indexStrs) {
                        tmpLayer =
                                (Layer) bodies.get(Integer.parseInt(indexStr));
                        layers.add(tmpLayer);
                        totalThickness += tmpLayer.thickness;
                    }

                    int rightSubstrate =
                            JDomUtils.getIntegerFromAttribute(
                                    geometryImplElement, "right_substrate");
                    layers.add(new Layer(bodies.get(rightSubstrate).material,
                            0.1));
                    totalThickness += 0.1;

                    // Create regions
                    MultiPlaneShape shape;
                    double[] surfaceNormal = Math2.Z_AXIS;
                    double[] layerNormal = Math2.MINUS_X_AXIS;
                    double[] origin = Math2.ORIGIN_3D;
                    double[] point =
                            Math2.multiply(-totalThickness / 2.0, Math2.X_AXIS);

                    IMaterialScatterModel material;
                    double thickness;

                    for (Layer layer : layers) {
                        thickness = layer.thickness;
                        material = layer.material;

                        shape =
                                MultiPlaneShape.createFilm(layerNormal, point,
                                        thickness);
                        shape.addPlane(surfaceNormal, origin); // surface
                        new Region(chamber, material, shape);

                        // Calculate next point
                        point =
                                Math2.plus(point,
                                        Math2.multiply(thickness, Math2.X_AXIS));
                    }

                    return extractAndApplyRotationTilt(geometryImplElement,
                            chamber);
                }

            };



    @Override
    public List<GeometryExtractor> getAllExtractors() {
        List<GeometryExtractor> extractors = new ArrayList<GeometryExtractor>();

        extractors.add(SUBSTRATE);
        extractors.add(MULTI_LAYERS);
        extractors.add(GRAIN_BOUNDARIES);

        return Collections.unmodifiableList(extractors);
    }

}
