package pymontecarlo.runner.nistmonte;

import gov.nist.microanalysis.EPQLibrary.Composition;
import gov.nist.microanalysis.EPQLibrary.EPQException;
import gov.nist.microanalysis.EPQLibrary.Material;
import gov.nist.microanalysis.EPQLibrary.ToSI;
import gov.nist.microanalysis.NISTMonte.BasicMaterialModel;
import gov.nist.microanalysis.NISTMonte.IMaterialScatterModel;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS.Region;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS.RegionBase;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS.TransformableRegion;
import gov.nist.microanalysis.Utility.Math2;

import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.jdom.Element;

import ptpshared.jdom.JDomUtils;

/**
 * Abstract class for the <code>GeometryExtractor</code> interface with added
 * helper methods.
 * 
 * @author ppinard
 */
public abstract class AbstractGeometryExtractor implements GeometryExtractor {

    /** XML tag for a body. */
    private static final String TAG_BODY = "pymontecarlo.input.base.body.Body";

    /** XML tag for a layer. */
    private static final String TAG_LAYER =
            "pymontecarlo.input.base.body.Layer";

    /**
     * Stores body information.
     * 
     * @author ppinard
     */
    protected static class Body {

        /** Material. */
        public final IMaterialScatterModel material;



        /**
         * Creates a <code>Body</code>.
         * 
         * @param material
         *            material
         */
        public Body(IMaterialScatterModel material) {
            if (material == null)
                throw new NullPointerException("material == null");
            this.material = material;
        }
    }

    /**
     * Stores layer information.
     * 
     * @author ppinard
     */
    protected static class Layer extends Body {

        /** Thickness of the layer (in meters). */
        public final double thickness;



        /**
         * Creates a <code>Layer</code>.
         * 
         * @param material
         *            material
         * @param thickness
         *            thickness (in meters)
         */
        public Layer(IMaterialScatterModel material, double thickness) {
            super(material);
            this.thickness = thickness;
        }
    }



    /**
     * Extracts the materials from a geometry XML element and returns a map
     * where the keys are the index of each material and the values are the
     * material scatter model of each material. The material scatter model
     * interface is used as the absorption energy of electron is automatically
     * set from the one specified in the material XML element.
     * 
     * @param geometryImplElement
     *            geometry XML element
     * @return map of material index and material scatter model
     * @throws EPQException
     *             if an exception occurs while creating the material scatter
     *             model
     */
    protected Map<Integer, IMaterialScatterModel> extractMaterials(
            Element geometryImplElement) throws EPQException {
        Map<Integer, IMaterialScatterModel> materials =
                new HashMap<Integer, IMaterialScatterModel>();

        Element materialsElement =
                JDomUtils.getChild(geometryImplElement, "materials");

        Element materialElement;
        int index;
        double density, absorptionEnergyElectron;
        Composition composition;
        Material material;
        IMaterialScatterModel scatterModel;
        for (Object obj : materialsElement.getChildren()) {
            materialElement = (Element) obj;

            index = JDomUtils.getIntegerFromAttribute(materialElement, "index");
            density =
                    JDomUtils
                            .getDoubleFromAttribute(materialElement, "density");
            absorptionEnergyElectron =
                    ToSI.eV(JDomUtils.getDoubleFromAttribute(materialElement,
                            "absorptionEnergyElectron"));

            composition = extractComposition(materialElement);
            material = new Material(composition, density);
            scatterModel = new BasicMaterialModel(material);
            scatterModel.setMinEforTracking(absorptionEnergyElectron);

            materials.put(index, scatterModel);
        }

        return materials;
    }



    /**
     * Extracts the composition from a material XML element.
     * 
     * @param materialElement
     *            material XML element
     * @return composition
     */
    protected Composition extractComposition(Element materialElement) {
        Element compositionElement =
                JDomUtils.getChild(materialElement, "composition");
        List<?> children = compositionElement.getChildren();

        gov.nist.microanalysis.EPQLibrary.Element[] elements =
                new gov.nist.microanalysis.EPQLibrary.Element[children.size()];
        double[] weightFractions = new double[children.size()];

        Element elementElement;
        int z;
        double weightFraction;
        for (int i = 0; i < children.size(); i++) {
            elementElement = (Element) children.get(i);

            z = JDomUtils.getIntegerFromAttribute(elementElement, "z");
            elements[i] =
                    gov.nist.microanalysis.EPQLibrary.Element.byAtomicNumber(z);

            weightFraction =
                    JDomUtils.getDoubleFromAttribute(elementElement,
                            "weightFraction");
            weightFractions[i] = weightFraction;
        }

        return new Composition(elements, weightFractions);
    }



    /**
     * Extracts and applies the rotation and tilt to the chamber.
     * 
     * @param geometryImplElement
     *            XML element
     * @param chamber
     *            region of the chamber as defined in <code>MonteCarloSS</code>
     */
    protected void extractAndApplyRotationTilt(Element geometryImplElement,
            Region chamber) {
        double[] pivot = Math2.ORIGIN_3D;
        double rotation =
                JDomUtils.getDoubleFromAttribute(geometryImplElement,
                        "rotation", 0.0);
        double tilt =
                JDomUtils.getDoubleFromAttribute(geometryImplElement, "tilt",
                        0.0);

        double phi = (rotation - Math.PI / 2.0) % (2.0 * Math.PI);
        double theta = tilt;
        double psi = Math.PI / 2.0;

        for (final RegionBase r : chamber.getSubRegions())
            if (r instanceof TransformableRegion)
                ((TransformableRegion) r).rotate(pivot, phi, theta, psi);
    }



    /**
     * Extracts bodies and layers from a geometry XML element.
     * 
     * @param geometryImplElement
     *            XML element
     * @param materials
     *            materials in the geometry. See
     *            {@link #extractMaterials(Element)}.
     * @return map of body index and {@link Body}
     * @throws IOException
     *             if an error occurs while reading the bodies
     */
    protected Map<Integer, Body> extractBodies(Element geometryImplElement,
            Map<Integer, IMaterialScatterModel> materials) throws IOException {
        Map<Integer, Body> bodies = new HashMap<Integer, Body>();

        Element bodiesElement =
                JDomUtils.getChild(geometryImplElement, "bodies");

        Element bodyElement;
        int index, materialIndex;
        double thickness;
        IMaterialScatterModel material;
        Body body;
        for (Object obj : bodiesElement.getChildren()) {
            bodyElement = (Element) obj;

            index = JDomUtils.getIntegerFromAttribute(bodyElement, "index");
            materialIndex =
                    JDomUtils.getIntegerFromAttribute(bodyElement, "material");
            material = materials.get(materialIndex);

            if (bodyElement.getName().equals(TAG_BODY)) {
                body = new Body(material);
            } else if (bodyElement.getName().equals(TAG_LAYER)) {
                thickness =
                        JDomUtils.getDoubleFromAttribute(bodyElement,
                                "thickness");
                body = new Layer(material, thickness);
            } else {
                throw new IOException("Unknown body implementation: "
                        + bodyElement.getName());
            }

            bodies.put(index, body);
        }

        return bodies;
    }

}
