package pymontecarlo.io.nistmonte;

import gov.nist.microanalysis.EPQLibrary.AlgorithmUser;
import gov.nist.microanalysis.EPQLibrary.EPQException;
import gov.nist.microanalysis.EPQLibrary.Strategy;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS.ElectronGun;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS.Region;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.jdom.Element;

import ptpshared.jdom.JDomUtils;

/**
 * Main extractor that extract all options from a options XML file.
 * 
 * @author ppinard
 */
public class OptionsExtractor implements Extractor {

    /**
     * Returns a default options extractor, where the default extractors have
     * been registered.
     * 
     * @return default options extractor
     */
    public static OptionsExtractor getDefault() {
        OptionsExtractor extractor = new OptionsExtractor();

        // Beam
        extractor.addBeamExtractor(new PencilBeamExtractor());
        extractor.addBeamExtractor(new GaussianFWHMBeamExtractor());

        // Geometry
        extractor.addGeometryExtractor(new SubstrateGeometryExtractor());
        extractor.addGeometryExtractor(new MultiLayersGeometryExtractor());
        extractor.addGeometryExtractor(new GrainBoundariesGeometryExtractor());

        // Models
        for (ModelExtractor modelExtrator : ModelExtractorFactory
                .getAllExtractors())
            extractor.addModelExtractor(modelExtrator);

        return extractor;
    }

    /** Available beam extractors. */
    private final List<BeamExtractor> beamExtractors;

    /** Available geometry extractors. */
    private final List<GeometryExtractor> geometryExtractors;

    /** Available model extractors. */
    private final List<ModelExtractor> modelExtractors;

    /** Result <code>MonteCarloSS</code>. */
    private MonteCarloSS mcss = null;

    /** XML tag. */
    private static final String TAG = "pymontecarlo.input.base.options.Options";



    /**
     * Creates a new <code>OptionsExtractor</code>.
     */
    public OptionsExtractor() {
        beamExtractors = new ArrayList<BeamExtractor>();
        geometryExtractors = new ArrayList<GeometryExtractor>();
        modelExtractors = new ArrayList<ModelExtractor>();
    }



    /**
     * Registers a new beam extractor.
     * 
     * @param extractor
     *            beam extractor
     */
    public void addBeamExtractor(BeamExtractor extractor) {
        if (extractor == null)
            throw new NullPointerException("extractor == null");
        beamExtractors.add(extractor);
    }



    /**
     * Registers a new geometry extractor.
     * 
     * @param extractor
     *            geometry extractor
     */
    public void addGeometryExtractor(GeometryExtractor extractor) {
        if (extractor == null)
            throw new NullPointerException("extractor == null");
        geometryExtractors.add(extractor);
    }



    /**
     * Registers a new model extractor.
     * 
     * @param extractor
     *            model extractor
     */
    public void addModelExtractor(ModelExtractor extractor) {
        if (extractor == null)
            throw new NullPointerException("extractor == null");
        modelExtractors.add(extractor);
    }



    /**
     * Extracts options from a options XML file.
     * 
     * @param optionsFile
     *            XML file
     * @throws IOException
     *             if an error occurs while reading the options XML file
     * @throws EPQException
     *             if an error occurs while setting up the options
     */
    public void extract(File optionsFile) throws IOException, EPQException {
        Element root = JDomUtils.loadXML(optionsFile).getRootElement();
        mcss = new MonteCarloSS();

        // Beam
        ElectronGun beam = extractBeam(root);
        mcss.setBeamEnergy(beam.getBeamEnergy());
        mcss.setElectronGun(beam);

        // Geometry
        extractGeometry(root, mcss.getChamber(), beam.getBeamEnergy());

        // Models
        Strategy strategy = new Strategy();
        extractModels(root, strategy);
        AlgorithmUser.applyGlobalOverride(strategy);
    }



    /**
     * Parses the XML options and returns the beam.
     * 
     * @param root
     *            XML options
     * @return electron beam
     * @throws IOException
     *             if an error occurs while reading the options
     * @throws EPQException
     *             if an error occurs while setting up the beam
     */
    protected ElectronGun extractBeam(Element root) throws IOException,
            EPQException {
        Element beamElement = JDomUtils.getChild(root, "beam");

        // Get beam implementation
        List<?> children = beamElement.getChildren();
        if (children.isEmpty())
            throw new IOException("No beam implementation found");

        Element beamImplElement = (Element) children.get(0);

        BeamExtractor extractor = getExtractor(beamImplElement, beamExtractors);
        return extractor.extract(beamImplElement);
    }



    /**
     * Parses the XML options and sets the geometry inside the chamber.
     * 
     * @param root
     *            XML options
     * @param chamber
     *            region of the chamber as defined in <code>MonteCarloSS</code>
     * @param beamEnergy
     *            beam energy (in joules)
     * @throws IOException
     *             if an error occurs while reading the options
     * @throws EPQException
     *             if an error occurs while setting up the geometry
     */
    protected void extractGeometry(Element root, Region chamber,
            double beamEnergy) throws IOException, EPQException {
        Element geometryElement = JDomUtils.getChild(root, "geometry");

        // Get geometry implementation
        List<?> children = geometryElement.getChildren();
        if (children.isEmpty())
            throw new IOException("No geometry implementation found");

        Element geometryImplElement = (Element) children.get(0);

        GeometryExtractor extractor =
                getExtractor(geometryImplElement, geometryExtractors);
        extractor.extract(geometryImplElement, chamber, beamEnergy);
    }



    /**
     * Parses the XML options and sets the models inside the strategy.
     * 
     * @param root
     *            XML options
     * @param strategy
     *            strategy of algorithms
     * @throws IOException
     *             if an error occurs while reading the options
     * @throws EPQException
     *             if an error occurs while setting up the strategy
     */
    protected void extractModels(Element root, Strategy strategy)
            throws IOException, EPQException {
        Element modelsElement = JDomUtils.getChild(root, "models");

        Element modelElement;
        ModelExtractor extractor;
        for (Object obj : modelsElement.getChildren()) {
            modelElement = (Element) obj;

            extractor = getExtractor(modelElement, modelExtractors);
            extractor.extract(modelElement, strategy);
        }
    }



    /**
     * Returns the extractor that can read the specified element.
     * 
     * @param <T>
     *            type of extractor
     * @param element
     *            XML element
     * @param extractors
     *            list of possible extractors
     * @return extractor
     * @throws IOException
     *             if no extractor is found or if more than one possibility is
     *             found
     */
    private <T extends Extractor> T getExtractor(Element element,
            List<T> extractors) throws IOException {
        List<T> possibilities = new ArrayList<T>();

        for (T extractor : extractors) {
            if (extractor.canExtract(element))
                possibilities.add(extractor);
        }

        if (possibilities.isEmpty())
            throw new IOException("No extractor was found for element: "
                    + element.getName());
        else if (possibilities.size() != 1)
            throw new IOException("Ambiguous. " + possibilities.size()
                    + " possibilities were found for element: "
                    + element.getName());

        return possibilities.get(0);
    }



    /**
     * Returns the <code>MonteCarloSS</code> after {@link #extract(File)} was
     * run.
     * 
     * @return <code>MonteCarloSS</code> read from options XML file
     */
    public MonteCarloSS getMonteCarloSS() {
        if (mcss == null)
            throw new RuntimeException("Call run(File) method first");
        return mcss;
    }



    @Override
    public boolean canExtract(Element element) {
        return element.getName().equals(TAG);
    }
}
