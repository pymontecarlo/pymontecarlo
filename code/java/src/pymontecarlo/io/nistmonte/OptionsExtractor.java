package pymontecarlo.io.nistmonte;

import gov.nist.microanalysis.EPQLibrary.AlgorithmUser;
import gov.nist.microanalysis.EPQLibrary.EPQException;
import gov.nist.microanalysis.EPQLibrary.Strategy;
import gov.nist.microanalysis.NISTMonte.BremsstrahlungEventListener;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS.ElectronGun;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS.Region;
import gov.nist.microanalysis.NISTMonte.XRayEventListener2;
import gov.nist.microanalysis.Utility.Math2;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.jdom.Element;

import ptpshared.jdom.JDomUtils;
import pymontecarlo.input.nistmonte.Detector;
import pymontecarlo.input.nistmonte.Limit;
import pymontecarlo.input.nistmonte.PhotonDetector;
import pymontecarlo.input.nistmonte.ScatteringDetector;

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

        for (BeamExtractor ex : new BeamExtractorFactory().getAllExtractors())
            extractor.addExtractor(ex);

        for (GeometryExtractor ex : new GeometryExtractorFactory()
                .getAllExtractors())
            extractor.addExtractor(ex);

        for (DetectorExtractor ex : new DetectorExtractorFactory()
                .getAllExtractors())
            extractor.addExtractor(ex);

        for (LimitExtractor ex : new LimitExtractorFactory().getAllExtractors())
            extractor.addExtractor(ex);

        for (ModelExtractor ex : new ModelExtractorFactory().getAllExtractors())
            extractor.addExtractor(ex);

        return extractor;
    }

    /** Available beam extractors. */
    private final List<BeamExtractor> beamExtractors;

    /** Available geometry extractors. */
    private final List<GeometryExtractor> geometryExtractors;

    /** Available detector extractors. */
    private final List<DetectorExtractor> detectorExtractors;

    /** Available limit extractors. */
    private final List<LimitExtractor> limitExtractors;

    /** Available model extractors. */
    private final List<ModelExtractor> modelExtractors;

    /** Name of the simulation. */
    private String name = null;

    /** Result <code>MonteCarloSS</code>. */
    private MonteCarloSS mcss = null;

    /** Extracted detectors. */
    private Map<String, Detector> detectors = null;

    /** Extracted limits. */
    private Set<Limit> limits = null;

    /** XML tag. */
    private static final String TAG = "pymontecarlo.input.base.options.Options";



    /**
     * Creates a new <code>OptionsExtractor</code>.
     */
    public OptionsExtractor() {
        beamExtractors = new ArrayList<BeamExtractor>();
        geometryExtractors = new ArrayList<GeometryExtractor>();
        detectorExtractors = new ArrayList<DetectorExtractor>();
        limitExtractors = new ArrayList<LimitExtractor>();
        modelExtractors = new ArrayList<ModelExtractor>();
    }



    /**
     * Registers an extractor.
     * 
     * @param extractor
     *            extrator
     */
    public void addExtractor(BeamExtractor extractor) {
        beamExtractors.add(extractor);
    }



    /**
     * Registers an extractor.
     * 
     * @param extractor
     *            extrator
     */
    public void addExtractor(GeometryExtractor extractor) {
        geometryExtractors.add(extractor);
    }



    /**
     * Registers an extractor.
     * 
     * @param extractor
     *            extrator
     */
    public void addExtractor(DetectorExtractor extractor) {
        detectorExtractors.add(extractor);
    }



    /**
     * Registers an extractor.
     * 
     * @param extractor
     *            extrator
     */
    public void addExtractor(LimitExtractor extractor) {
        limitExtractors.add(extractor);
    }



    /**
     * Registers an extractor.
     * 
     * @param extractor
     *            extrator
     */
    public void addExtractor(ModelExtractor extractor) {
        modelExtractors.add(extractor);
    }



    /**
     * Creates a new <code>MonteCarloSS</code>.
     * 
     * @return a new <code>MonteCarloSS</code>
     */
    protected MonteCarloSS createMonteCarloSS() {
        return new MonteCarloSS();
    }



    /**
     * Extracts options from a options XML element.
     * 
     * @param root
     *            options XML element
     * @throws IOException
     *             if an error occurs while reading the options XML element
     * @throws EPQException
     *             if an error occurs while setting up the options
     */
    public void extract(Element root) throws IOException, EPQException {
        mcss = createMonteCarloSS();

        // ///////
        // Name //
        // ///////
        name = JDomUtils.getStringFromAttribute(root, "name");

        // ///////
        // Beam //
        // ///////
        ElectronGun beam = extractBeam(root);
        mcss.setBeamEnergy(beam.getBeamEnergy());
        mcss.setElectronGun(beam);

        // ///////////
        // Geometry //
        // ///////////
        double[] normal =
                extractGeometry(root, mcss.getChamber(), beam.getBeamEnergy());

        // /////////////
        // Detectors //
        // /////////////
        detectors = extractDetectors(root, mcss);

        // Surface plane
        for (Detector detector : detectors.values()) {
            if (detector instanceof ScatteringDetector) {
                ((ScatteringDetector) detector).setSurfacePlane(normal,
                        Math2.ORIGIN_3D);
            }
        }

        // Detector position
        double[] detectorPosition = null;
        boolean requiresBremsstrahlung = false;
        for (Detector detector : detectors.values()) {
            if (detector instanceof PhotonDetector) {
                detectorPosition =
                        ((PhotonDetector) detector).getDetectorPosition();
                requiresBremsstrahlung =
                        requiresBremsstrahlung
                                || ((PhotonDetector) detector)
                                        .requiresBremsstrahlung();
            }
        }

        // X-ray event listener
        XRayEventListener2 xrel = null;
        if (detectorPosition != null) {
            xrel = new XRayEventListener2(mcss, detectorPosition);
            mcss.addActionListener(xrel);
        }

        BremsstrahlungEventListener bel = null;
        if (detectorPosition != null && requiresBremsstrahlung) {
            bel = new BremsstrahlungEventListener(mcss, detectorPosition);
            mcss.addActionListener(bel);
        }

        // Setup
        for (Detector detector : detectors.values())
            detector.setup(mcss, xrel, bel);

        // /////////
        // Limits //
        // /////////
        limits = extractLimits(root, mcss);
        for (Limit limit : limits)
            limit.setup(mcss, xrel, bel);

        // /////////
        // Models //
        // /////////
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
     * @return surface plane normal
     */
    protected double[] extractGeometry(Element root, Region chamber,
            double beamEnergy) throws IOException, EPQException {
        Element geometryElement = JDomUtils.getChild(root, "geometry");

        // Get geometry implementation
        List<?> children = geometryElement.getChildren();
        if (children.isEmpty())
            throw new IOException("No geometry implementation found");

        Element geometryImplElement = (Element) children.get(0);

        GeometryExtractor extractor =
                getExtractor(geometryImplElement, geometryExtractors);
        return extractor.extract(geometryImplElement, chamber, beamEnergy);
    }



    /**
     * Parses the XML options and returns the detectors.
     * 
     * @param root
     *            XML options
     * @param mcss
     *            Monte Carlo simulation
     * @return map of detector and their key name
     * @throws IOException
     *             if an error occurs while reading the options
     * @throws EPQException
     *             if an error occurs while setting up the detectors
     */
    protected Map<String, Detector> extractDetectors(Element root,
            MonteCarloSS mcss) throws IOException, EPQException {
        Element detectorsElement = JDomUtils.getChild(root, "detectors");

        Map<String, Detector> detectors = new HashMap<String, Detector>();

        Element detectorElement;
        DetectorExtractor extractor;
        String key;
        Detector detector;
        for (Object obj : detectorsElement.getChildren()) {
            detectorElement = (Element) obj;

            key = JDomUtils.getStringFromAttribute(detectorElement, "_key");

            extractor = getExtractor(detectorElement, detectorExtractors);
            detector = extractor.extract(detectorElement);

            detectors.put(key, detector);
        }

        return detectors;
    }



    /**
     * Parses the XML options and returns the limits.
     * 
     * @param root
     *            XML options
     * @param mcss
     *            Monte Carlo simulation
     * @return limits
     * @throws IOException
     *             if an error occurs while reading the options
     * @throws EPQException
     *             if an error occurs while setting up the limits
     */
    protected Set<Limit> extractLimits(Element root, MonteCarloSS mcss)
            throws IOException, EPQException {
        Element limitsElement = JDomUtils.getChild(root, "limits");

        Set<Limit> limits = new HashSet<Limit>();

        Element limitElement;
        LimitExtractor extractor;
        Limit limit;
        for (Object obj : limitsElement.getChildren()) {
            limitElement = (Element) obj;

            extractor = getExtractor(limitElement, limitExtractors);
            limit = extractor.extract(limitElement);

            limits.add(limit);
        }

        return limits;
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
     * Returns the name of the simulation.
     * 
     * @return name of the simulation
     * @throws RuntimeException
     *             if {@link #extract(File)} was not run.
     */
    public String getName() {
        if (name == null)
            throw new RuntimeException("Call extract(File) method first");
        return name;
    }



    /**
     * Returns the <code>MonteCarloSS</code> after {@link #extract(File)} was
     * run.
     * 
     * @return <code>MonteCarloSS</code> read from options XML file
     * @throws RuntimeException
     *             if {@link #extract(File)} was not run.
     */
    public MonteCarloSS getMonteCarloSS() {
        if (mcss == null)
            throw new RuntimeException("Call extract(File) method first");
        return mcss;
    }



    /**
     * Returns the <code>Detector</code>'s after {@link #extract(File)} was run.
     * 
     * @return detectors read from options XML file
     * @throws RuntimeException
     *             if {@link #extract(File)} was not run.
     */
    public Map<String, Detector> getDetectors() {
        if (detectors == null)
            throw new RuntimeException("Call extract(File) method first");
        return Collections.unmodifiableMap(detectors);
    }



    /**
     * Returns the <code>Limit</code>'s after {@link #extract(File)} was run.
     * 
     * @return limits read from options XML file
     * @throws RuntimeException
     *             if {@link #extract(File)} was not run.
     */
    public Set<Limit> getLimits() {
        if (limits == null)
            throw new RuntimeException("Call extract(File) method first");
        return Collections.unmodifiableSet(limits);
    }



    @Override
    public boolean canExtract(Element element) {
        return element.getName().equals(TAG);
    }

}
