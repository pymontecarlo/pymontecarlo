package pymontecarlo.io.nistmonte;

import gov.nist.microanalysis.EPQLibrary.ToSI;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS.ElectronGun;
import gov.nist.microanalysis.NISTMonte.PencilBeam;

import org.jdom.Element;

import ptpshared.jdom.JDomUtils;

/**
 * Abstract class for the <code>BeamExtractor</code> interface with added helper
 * methods.
 * 
 * @author ppinard
 */
public abstract class AbstractBeamExtractor implements BeamExtractor {

    /**
     * Extracts the beam position position from the XML element and sets it for
     * the beam.
     * 
     * @param beamImplElement
     *            XML element
     * @param beam
     *            beam
     */
    protected void extractBeamEnergy(Element beamImplElement, ElectronGun beam) {
        double energy =
                ToSI.eV(JDomUtils.getDoubleFromAttribute(beamImplElement,
                        "energy"));
        beam.setBeamEnergy(energy);
    }



    /**
     * Extracts the center position from the XML element and sets it for the
     * beam.
     * 
     * @param beamImplElement
     *            XML element
     * @param beam
     *            beam
     */
    protected void extractCenter(Element beamImplElement, ElectronGun beam) {
        Element centerElement = JDomUtils.getChild(beamImplElement, "origin");
        double x = JDomUtils.getDoubleFromAttribute(centerElement, "x");
        double y = JDomUtils.getDoubleFromAttribute(centerElement, "y");
        double z = JDomUtils.getDoubleFromAttribute(centerElement, "z");
        beam.setCenter(new double[] { x, y, z });
    }



    /**
     * Extracts the direction from the XML element and sets it for the beam.
     * 
     * @param beamImplElement
     *            XML element
     * @param beam
     *            beam
     */
    protected void extractDirection(Element beamImplElement, PencilBeam beam) {
        Element directionElement =
                JDomUtils.getChild(beamImplElement, "direction");
        double u = JDomUtils.getDoubleFromAttribute(directionElement, "x");
        double v = JDomUtils.getDoubleFromAttribute(directionElement, "y");
        double w = JDomUtils.getDoubleFromAttribute(directionElement, "z");
        beam.setDirection(new double[] { u, v, w });
    }

}
